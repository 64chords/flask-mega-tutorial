import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir,"app.db")
    # signal the application every time a change is about to be made in the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    mail server settings
    以下の項目を含む：
    ・サーバー、ポート、暗号化の有無、ユーザー名、パスワード
    """
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    #ポート：デフォルトは25とする
    MAIL_POST = int(os.environ.get("MAIL_POST") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    #リスト内のアドレス全員に送信される
    ADMINS = ["tmgf.15.su@gmail.com"]
