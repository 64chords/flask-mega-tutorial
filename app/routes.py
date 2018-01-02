# -*- encoding: utf-8 -*-
from flask import render_template, flash, redirect, url_for,request
from flask_login import current_user,login_user,logout_user,login_required
from app import app,db
from app.forms import LoginForm,RegistrationForm
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
