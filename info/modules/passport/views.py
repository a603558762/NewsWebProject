from flask import request, current_app, make_response

from info import redis_store
from info.constants import IMAGE_CODE_REDIS_EXPIRES
from info.utils.captcha.captcha import captcha
from . import passport_blu


@passport_blu.route('/image/captch_img/<id>')
def get_image_code(id):
    # 获取captchid
    print(id)
    current_app.logger.debug(id)
    # 随机生成验证码图形,这是生成验证码的模块的内容
    # text参数是验证码的文字captch_img 是生成的验证码信息,可以直接返回的验证码信息
    name, text, captch_img=captcha.generate_captcha()
    # 将验证码存入到redis
    try:

        redis_store.set(id,text,ex=IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.debug(e)
    print(name)
    print(text)


    # 修改链接类型Content-Type,将验证码图形发送给前端
    response=make_response(captch_img)
    response.headers['Content-Type']='image/jpg'
    # pass
    return response
