from flask import Flask, render_template
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session

app = Flask(__name__)
manager=Manager(app)


# 配置文件
class Config(object):
    DEBUG=True
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

app.config.from_object(Config)
db=SQLAlchemy(app)

Migrate(app,db)

manager.add_command('db',MigrateCommand)

# 配置redis
redis_store=StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# 开启CSRF保护
CSRFProtect(app)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    manager.run()