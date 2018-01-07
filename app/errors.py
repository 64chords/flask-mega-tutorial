# -*- encoding: utf-8 -*-
"""
エラーハンドリング用
@app.errorhandlerデコレータで例外をキャッチできる
returnではtemplateの他、エラーコードを返す
（正常(エラーコード：200)の場合、エラーコードは不要）
"""

from flask import render_template
from app import app,db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_error(error):
    """
    internal server error( = error code:500)が
    発生する条件には、DB関連のものも含まれる
        ex) uniqueが満たされないなど
    ので、dbをロールバックしたほうが良い
    """
    # dbのロールバック
    db.session.rollback()
    return render_template('500.html'),500
