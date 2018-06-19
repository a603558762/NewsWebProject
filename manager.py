from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

app = Flask(__name__)

class Config(object):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql://root:hh123456@localhost3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # redis配置
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379

app.config.from_object(Config)
db=SQLAlchemy(app)

# 配置redis
redis_store=StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# 开启CSRF保护
CSRFProtect(app)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()