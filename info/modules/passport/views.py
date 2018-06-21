import errno
import random

from flask import request, current_app, make_response, jsonify, json

from info import redis_store
from info.constants import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES
from info.libs.yuntongxun.sms import CCP
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
    # 判断图形验证码是否正确
    input_captcha_id = param_dict['input_captch']
    img_captcha_id = 'captch_id' + param_dict['uuid']
    phone_num = param_dict['mobile']
    try:
        real_captcha_id = redis_store.get(img_captcha_id).decode()
    except Exception as e:
        current_app.logger.debug(e)

    print(input_captcha_id)
    if input_captcha_id.upper() != real_captcha_id.upper():
        return jsonify(errno=RET.DBERR, errmsg="验证码错误")
    # 验证码是否过期
    if not real_captcha_id:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    # 发送短信本地随机生成短信验证码
    randam_smscode= ''.join(str(i) for i in random.sample(range(0, 9), 6))
    print(randam_smscode)
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
