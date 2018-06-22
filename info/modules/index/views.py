import logging

from flask import session, render_template, current_app, request, jsonify

# from info import redis_store
from info.models import User
from . import Index_blu
from info import redis_store

@Index_blu.route('/')
def index():

    # redis_store.set('name','zhouhao')
    redis_store.set('name','hao')
    # 使用session设置sid的session是从from flask import session导入的
    # 设置session位置保存的时候使用的是:TODO from flask_session import Session
    # 通过浏览器的cookie来判断是不是已经登录的用户


    nick_name=session.get("nick_name",None)
    # print(user_id)
    # print(mobile)
    # print(nick_name)

    # if not all([user_id,mobile,nick_name]):
    #     print('不是用户登录')
    #     return render_template('news/index.html')

    user = None
    try:
        user=User.query.filter(User.nick_name==nick_name).first()
    except Exception as e:
        current_app.logger.debug(e)


    data={
        "user":user.to_dict() if user else None
    }
    print(data)

    print('用户已登录')

    return render_template('news/index.html',data=data)



@Index_blu.route('/favicon.ico')
def favicon():
    # 固定写法,每个网站都是固定的写法有这个favicon.ico
    return current_app.send_static_file('news/favicon.ico')