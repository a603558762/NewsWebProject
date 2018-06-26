import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, csrf
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis
from config import Config, config
# from info.modules.index import Index_blu


db = SQLAlchemy()
redis_store=1  # type: StrictRedis
sess = Session()
# csrf = CSRFProtect()

# 以前的初始化的代码都是在__init__文件中的
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 抽取app + db延迟初始化,在使用蓝图的地方导出蓝图
    db.init_app(app)

    global redis_store
    # 使用这个redis_store进行数据操作,config里面的SESSION_REDIS是做配置用的,配置存储的位置用
    # session的使用也有两个,一个是做配置
    redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT,decode_responses=True)

    from info.modules.index import Index_blu

    # 主页蓝图注册的导入
    app.register_blueprint(Index_blu)

    # passport_blu 蓝图注册
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)


    # new_blu注册
    from info.modules.news_detail import news_blu
    app.register_blueprint(news_blu)

    # 个人中心
    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)

    # 创建自定义的过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class,'do_index_class')
    # 防止CSRF跨站伪造
    CSRFProtect(app)

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response
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
