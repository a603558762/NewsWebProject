import logging

from flask import session, render_template, current_app

# from info import redis_store
from . import Index_blu
from info import redis_store

@Index_blu.route('/')
def index():

    redis_store.set('name','zhouhao')
    # 使用session设置sid的session是从from flask import session导入的
    # 设置session位置保存的时候使用的是:TODO from flask_session import Session
    session['aaa']='wangwnagban'

    # logging.debug('错误1111')
    return render_template('news/index.html')



@Index_blu.route('/favicon.ico')
def favicon():
    # 固定写法,每个网站都是固定的写法有这个favicon.ico
    return current_app.send_static_file('news/favicon.ico')