import errno
import random
import re
from datetime import datetime

from flask import request, current_app, make_response, jsonify, json, session

from info import redis_store, db
from info.constants import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu


@passport_blu.route('/image/captch_img/<id>')
def get_image_code(id):
    # 获取captchid
    print(id)
    current_app.logger.debug(id)
    # 随机生成验证码图形,这是生成验证码的模块的内容
    # text参数是验证码的文字captch_img 是生成的验证码信息,可以直接返回的验证码信息
    name, text, captch_img = captcha.generate_captcha()
    # 将验证码存入到redis
    try:

        redis_store.set(id, text, ex=IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.debug(e)
    print(name)
    print(text)

    # 修改链接类型Content-Type,将验证码图形发送给前端
    response = make_response(captch_img)
    response.headers['Content-Type'] = 'image/jpg'
    # pass
    return response


@passport_blu.route('/image/check', methods=['POST'])
def check_captch_id():
    # 获取传入的uuid,手机号,输入的验证码
    param_dict = json.loads(request.data)
    # print(param_dict)
    # print(param_dict)
    # 判断图形验证码是否正确
    input_captcha_id = param_dict['input_captch']
    img_captcha_id = 'captch_id' + param_dict['uuid']
    phone_num = param_dict['mobile']
    try:
        real_captcha_id = redis_store.get(img_captcha_id)
    except Exception as e:
        current_app.logger.debug(e)

    print(input_captcha_id)
    if input_captcha_id.upper() != real_captcha_id.upper():
        return jsonify(errno=RET.DBERR, errmsg="验证码错误")
    # 验证码是否过期
    if not real_captcha_id:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")
    # 验证手机好:
    # if not re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\\d{8}$',phone_num):
    #     return jsonify(errno=RET.DATAERR, errmsg="手机号错误")
    # 发送短信本地随机生成短信验证码
    randam_smscode = ''.join(str(i) for i in random.sample(range(0, 9), 6))
    print(randam_smscode)
    try:
        redis_store.set('mobile' + phone_num, randam_smscode, ex=SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.debug(e)
    # # 导入云通讯平台,电信的服务发送短信
    # sms_status=CCP().send_template_sms(to=18506255964,datas=[randam_smscode,SMS_CODE_REDIS_EXPIRES/60],temp_id=1)
    # if sms_status==0:
    #     print('发送成功')
    #     return jsonify(errno=RET.OK, errmsg="发送成功")
    # elif sms_status==-1:
    #     print('电信发送失败')
    # else:
    #     print('未知错误')

    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route('/register', methods=['post'])
def register():
    register_data = request.json
    print("register_data:", register_data)
    mobile = register_data['mobile']
    smscode = register_data['smscode']
    password = register_data['password']
    # return jsonify(errno=RET.OK, errmsg="注册成功")
    # 判空
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 验证smscode是否正确:
    real_smscode = None
    try:
        real_smscode = redis_store.get('mobile' + mobile)
    except Exception as e:
        current_app.logger.log(e)
    if not real_smscode:
        return jsonify(errno=RET.DBERR, errmsg="短信已过期")
    if real_smscode != smscode:
        return jsonify(errno=RET.DBERR, errmsg="短信验证码错误")
    # 查询手机已注册
    isregistered = None
    try:
        isregistered = User.query.filter(User.nick_name == mobile).first()
        print(isregistered)
    except Exception as e:
        current_app.logger.debug(e)
    if isregistered:
        return jsonify(errno=RET.DBERR, errmsg="该手机已注册")

    # 注册到数据库
    try:
        user = User()
        user.nick_name = mobile
        user.mobile = mobile
        user.password = password
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(e)
        return jsonify(errno=RET.SERVERERR, errmsg="内部错误")
    print('注册成功')
    try:
        redis_store.delete('' + mobile)
    except Exception as e:
        current_app.logger.debug(e)

    # 注册后添加SESSION
    session['nick_name'] = mobile
    session["user_id"] = mobile
    session["mobile"] = mobile


    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/login', methods=['post'])
def login():
    # 获得到参数
    login_data = request.json
    mobile = login_data['mobile']
    password = login_data['password']
    print(login_data)
    # 查询用户名和密码
    user = None
    try:
        # 查询到的一个对象
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.debug(e)

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户名不存在")
    # 验证密码是否正确
    ispassword = None
    try:
        # 查询到的是ret的password是否正确,所以传入的是ret
        ispassword = User.check_passowrd(user, password=password)
        print(ispassword)
    except Exception as e:
        current_app.logger.debug(e)
    if not ispassword:
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 登录成功后,设置session
    # response=make_response()
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin
    # 设置用户最后一次的登录时间
    user.last_login = datetime.now()
    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route('/logout')
def logout():
    # 退出后清理session,刷新页面
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)

    return jsonify(errno=RET.OK, errmsg="退出成功")
