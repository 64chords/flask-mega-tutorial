# -*- encoding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = dict(username="64chords")
    posts = [
        dict(author=dict(username="user1"),body="hello!"),
        dict(author=dict(username="user2"),body="good night!")
    ]
    return render_template("index.html",title="Home",user=user,posts=posts)

@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        """
        GETの時は常にFalseとなる。
        POSTの時、form内で定義されたValidatorが実行され、全部OKの場合のみTrue
        """
        flash("Login requested for user {}, remember_me={}".format(
            form.username.data,form.remember_me.data
        ))
        return redirect(url_for("index"))
    return render_template('login.html',title="Sign In",form=form)
