import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

# from info.modules.index import Index_blu

from config import Config, config

# from info.modules.index import Index_blu

db = SQLAlchemy()
redis_store=None  # type: StrictRedis
sess = Session()


# 以前的初始化的代码都是在__init__文件中的
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 抽取app + db延迟初始化,在使用蓝图的地方导出蓝图
    db.init_app(app)

    global redis_store
    redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

    from info.modules.index import Index_blu
    # 蓝图注册
    app.register_blueprint(Index_blu)

    # 防止CSRF跨站伪造
    CSRFProtect(app)
    # 将session保存到redis
    sess.init_app(app)
    setup_log(config_name)
    return app

def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)




# 配置redis

# 开启CSRF保护







# 蓝图注册
