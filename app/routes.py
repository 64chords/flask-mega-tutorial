# -*- encoding: utf-8 -*-
from datetime import datetime
from flask import render_template, flash, redirect, url_for,request
from flask_login import current_user,login_user,logout_user,login_required
from app import app,db
from app.forms import LoginForm,RegistrationForm,EditProfileForm
from app.models import User

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        dict(author=dict(username="user1"),body="hello!"),
        dict(author=dict(username="user2"),body="good night!")
    ]
    return render_template("index.html",title="Home",posts=posts)

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
    """
    first_or_404()：クエリの結果が存在しなければ404エラーを送出する
    """
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        dict(author=user,body="Test post #1"),
        dict(author=user,body="Test post #2")
    ]
    return render_template("user.html",user=user,posts=posts)

@app.route('/edit_profile',methods=["GET","POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
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
