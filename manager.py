from flask import Flask, render_template
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session
from config import Config
app = Flask(__name__)
manager=Manager(app)




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