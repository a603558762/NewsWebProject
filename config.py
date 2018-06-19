# 配置文件
from redis import StrictRedis


class Config(object):
    DEBUG=True
    SECRET_KEY='gsfdfhdfgdhfh'
    SQLALCHEMY_DATABASE_URI='mysql://root:hh123456@localhost3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # redis配置
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379
    # Session 配置
    SESSION_TYPE='redis'
    # 开启签名
    SESSION_USE_SIGNER=True
    # 设置redis初始对象
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)


    # 设置过期时间
    SESSION_PERMANENT=False