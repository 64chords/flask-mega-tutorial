# -*- encoding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired,ValidationError,Email,EqualTo,Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password',validators=[DataRequired(),EqualTo("password")]
    )
    submit = SubmitField("Register")

    """
    オプションのバリデータ
    validate_<field_name>により追加できる
    ex) validate_usernameなら、user_nameのvalidatorsに追加される
    """
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("please use a different username.")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("please use a different email address.")

class EditProfileForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    about_me = TextAreaField('Aboutme',validators=[Length(min=0,max=140)])
    submit = SubmitField("Submit")

    def __init__(self,original_username,*args,**kwargs):
        #コンストラクタのオーバーロード
        super(EditProfileForm,self).__init__(*args,**kwargs)
        self.original_username = original_username

    def validate_username(self,username):
        """
        usernameのオプションバリデータ
        もし元々のユーザー名と異なる場合はDBに存在するかチェック
        """
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")

class PostForm(FlaskForm):
    post = TextAreaField("Say something",validators=[DataRequired()])
    submit = SubmitField("Submit")
