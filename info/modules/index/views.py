import logging

from flask import session

from info import redis_store
from . import Index_blu

@Index_blu.route('/')
def index():
    redis_store.set('name','zhouhao')
    # 使用session设置sid的session是从from flask import session导入的
    # 设置session位置保存的时候使用的是:TODO from flask_session import Session
    session['aaa']='wangwnagban'

    # logging.debug('错误1111')





    return 'indexssssss'