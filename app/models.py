# -*- encoding: utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from time import time
from hashlib import md5
from flask_login import UserMixin
import jwt
from app import db,login,app

"""
current_user変数を参照した際に
呼ばれるコールバック関数
"""
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# フォロワー補助テーブル モデルの概念が不要のためクラスは作成しない
followers = db.Table(
    "followers",
    db.Column("follower_id",db.Integer,db.ForeignKey("user.id")),
    db.Column("followed_id",db.Integer,db.ForeignKey("user.id"))
)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120),index=True,unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)
    """
    a db.relationship field is normally defined on the “one” side, and
    is used as a convenient way to get access to the “many”.
    """
    posts = db.relationship("Post",backref="author",lazy="dynamic")
    """
    フォロー・フォロワーの関係を追加
    "User": セルフ参照の関係なので自分自身
    secondary: 関係性を表す関係テーブル
    followers.c.**: cはColumnsを表すプロパティ
    詳細はp.134~135を参照のこと（８．３節）
    """
    followed = db.relationship(
        "User",secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers",lazy="dynamic"),lazy="dynamic"
    )

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def avatar(self,size):
        """
        gravatar.comよりemailのハッシュをキーとして
        identiconの画像をGETするURLを生成
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".\
            format(digest,size)

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):
        """
        filter()とfilter_by()の違い：
            filter_by:上級。カラム名との一致を見る
            filter:低級。任意の条件を使用できる。一定値との比較のみ可
        """
        # followersテーブルのfollow_idカラムと、ユーザーIDが一致する個数をカウント
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        フォローしてる人のポストを取得
        詳細は8.6.1節(pp.142〜)を参照
        """
        #フォローしてる人のポスト
        followed = Post.query.join(
            followers,(followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        #自分自身のポスト
        own = Post.query.filter_by(user_id=self.id)
        #結合し、時系列に並べ替え
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self,expires_in=600):
        """
        decode('utf-8')は必須∵jwt.encode()はトークンをバイトでリターンするため、
        文字列で扱いたい
        """
        return jwt.encode(
            {"reset_password":self.id,"exp":time() + expires_in},
            app.config["SECRET_KEY"],algorithm="HS256").decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token,app.config["SECRET_KEY"],
                algorithms=["HS256"])["reset_password"]
        except:
            return
        return User.query.get(id)


    def __repr__(self):
        return "<User {}>".format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Post {}>".format(self.body)
