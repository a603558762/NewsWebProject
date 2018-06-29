from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from config import  config
from info import create_app,db
from info import models

# 抽取的结果在Manager中只有执行工厂模式和数据库的迁移的工作是在Manager里面完成的
from info.models import User

app=create_app('dev')
manager=Manager(app)
Migrate(app,db)
manager.add_command('db',MigrateCommand)
# 集成日志到项目中取  logging模块 .keepgit

# 创建命令行:
@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def create_admin(name, password):
    if not all([name,password]):
        print('参数不全')
        return
    try:
        user=User()
        user.mobile=name
        user.nick_name=name
        user.password=password
        user.is_admin=True
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(e)
        return
    print('创建管理员成功')



if __name__ == '__main__':
    # print(app.url_map)
    manager.run()

