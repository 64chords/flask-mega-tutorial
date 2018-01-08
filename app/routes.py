# -*- encoding: utf-8 -*-
from datetime import datetime
from flask import render_template, flash, redirect, url_for,request
from flask_login import current_user,login_user,logout_user,login_required
from app import app,db
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm
from app.models import User,Post

@app.route('/',methods=["GET","POST"])
@app.route('/index',methods=["GET","POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live:")
        """
        note: リダイレクト(GETメソッド)でindexページへ。
        POSTはリダイレクトでGETによりページを表示することで、
        ブラウザ更新時のPOST再実行を防止することが出来る。
        詳しくはPRGパターン(Post/Redirect/Get)を参照のこと。
        """
        return redirect(url_for("index"))
    # page引数の値を取得する　無ければ1
    page = request.args.get("page",1,type=int)
    # posts = current_user.followed_posts().all()  #重い
    """
    paginateメソッドの引数：ページ番号、最大アイテム数、エラーフラグ
    詳しくはpp.159参照 戻り値はpaginationオブジェクト
    """
    posts = current_user.followed_posts().paginate(
        page,app.config["POSTS_PER_PAGE"],False)
    """
    paginationオブジェクトが前後を参照できる場合それを取得し、
    url_forメソッドによりリンクを生成する。生成時はpage引数にページ番号を含める
    """
    next_url = url_for('index',page=posts.next_num)\
        if posts.has_next else None
    prev_url = url_for('index',page=posts.prev_num)\
        if posts.has_prev else None
    return render_template("index.html",title="Home",form=form,
        posts=posts.items,next_url=next_url,prev_url=prev_url)

@app.route('/login',methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        #認証済みの場合、トップページへ
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        """
        GETの時は常にFalseとなる。
        POSTの時、form内で定義されたValidatorが実行され、全部OKの場合のみTrue
        """
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # ユーザーの存在有無とパスワードのチェック
            flash("invalid username or password.")
            return redirect(url_for('login'))
        # rememberするか否かをチェックボックスから取得
        # login_user()を実行することで、この先current_user変数にユーザーの情報がセットされる
        login_user(user,remember=form.remember_me.data)

        """
        @login_required decorator will intercept the request and
        respond with a redirect to /login, but it will add a query
        string argument to this URL, making the complete redirect
        URL /login?next=/index.
        """
        # “the request.args attribute exposes the contents of the query string in a friendly dictionary format.”
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            next_page = url_for("index")

        return redirect(next_page)

    # GETの場合実行される。Sign Inのページを表示するだけ
    return render_template('login.html',title="Sign In",form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html",title="Register",form=form)

"""
@app.routeデコレータは変数を含むことが可能。<>で括る
ex) /user/susanとした場合、usernameに"susan"がセットされる
"""
@app.route('/user/<username>')
@login_required
def user(username):
    # first_or_404()：クエリの結果が存在しなければ404エラーを送出する
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page",1,type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,app.config["POSTS_PER_PAGE"],False)
    next_url = url_for("user",username=username,page=posts.next_num)\
        if posts.has_next else None
    prev_url = url_for("user",username=username,page=posts.prev_num)\
        if posts.has_prev else None
    return render_template("user.html",user=user,posts=posts.items,
        next_url=next_url,prev_url=prev_url)

@app.route('/edit_profile',methods=["GET","POST"])
@login_required
def edit_profile():
    # プロフィールの編集
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        """
        form.validate_on_submit()は以下の２つのケースでFalseとなる：
            １：GETメソッド
            ２：バリデーション失敗
        １の場合ならば、current_userの情報を使ってフォームを埋める
        ２の場合ならばそのまま（WTFがフォームの情報を持っている。そのままにする）
        """
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html",title="Edit Profile",form=form)

@app.route("/follow/<username>")
@login_required
def follow(username):
    """フォローする"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found".format(username))
        return redirect(url_for("index"))
    current_user.follow(user)
    db.session.commit()
    flash("You are following {}:".format(username))
    return redirect(url_for("user",username=username))

@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    """フォロー解除"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found.".format(username))
        return redirect(url_for("index"))
    if user == current_user:
        flash("You cannot unfollow yourself.")
        return redirect(url_for("user",username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You are not following {}".format(username))
    return redirect(url_for("user",username=username))

@app.route("/explore")
@login_required
def explore():
    """全ユーザの投稿を表示する(所謂タイムライン表示)"""
    page = request.args.get("page",1,type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,app.config["POSTS_PER_PAGE"],False)
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    next_url = url_for('index',page=posts.next_num)\
        if posts.has_next else None
    prev_url = url_for('index',page=posts.prev_num)\
        if posts.has_prev else None
    """
    index.htmlと大差ないため、レンダリングで使用する。
    postフォームは不要のため、引数には含めない。
    """
    return render_template("index.html",title="Explore",posts=posts.items,
        next_url=next_url,prev_url=prev_url)

"""
@app.before_requestデコレータ：
view functionが実行される前に実施されるメソッドを定義できる
"""
@app.before_request
def before_request():
    if current_user.is_authenticated:
        # 認証済みなら現在時刻をDBにセットする
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
