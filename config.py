# 配置文件
from logging import ERROR, WARNING

from redis import StrictRedis





class Config(object):
    # HOST='0.0.0.0'
    # PORT=8080
    # SQLALCHEMY配置
    SECRET_KEY='gsfdfhdfgdhfh'
    SQLALCHEMY_DATABASE_URI='mysql://root:hh123456@localhost:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    # redis配置
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379

    # Session 配置存储到redis
    SESSION_TYPE='redis'
    # 开启签名
    SESSION_USE_SIGNER=True
    # 设置redis初始对象
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)


    # 设置过期时间
    SESSION_PERMANENT=False

# 在不同环境下的配置,开发,生产,测试
class Dev(Config):
    DEBUG = True
    LOG_LEVEL=DEBUG


class Production(Config):
    DEBUG = True
    LOG_LEVEL = WARNING


class TestingConfig(Config):
    DEBUG=True
    LOG_LEVEL=ERROR

config={
    'dev':Dev,
    'production':Production,
    'testingconfig':TestingConfig
}