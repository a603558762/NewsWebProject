
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from config import  config
from info import create_app,db
from info import models

# 抽取的结果在Manager中只有执行工厂模式和数据库的迁移的工作是在Manager里面完成的

app=create_app('dev')
manager=Manager(app)
Migrate(app,db)
manager.add_command('db',MigrateCommand)
# 集成日志到项目中取  logging模块 .keepgit


if __name__ == '__main__':
    # print(app.url_map)
    manager.run()
