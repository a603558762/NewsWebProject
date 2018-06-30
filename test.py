import random
from time import mktime, asctime, localtime, strftime



from info import db
from info.models import User
from manager import app

date1 = (2018, 5, 1, 0, 0, 0, -1, -1, -1)
time1 = mktime(date1)
date2 = (2018, 6, 1, 0, 0, 0, -1, -1, -1)
time2 = mktime(date2)
# 在这一范围内生成随机数
# random_time = random.uniform(time1, time2)  # uniform返回随机实数 time1 <= time < time2
# t1=asctime(localtime(random_time))

date3 = (2018, 6, 1, 0, 0, 0, -1, -1, -1)
time3 = mktime(date3)
date4 = (2018, 7, 1, 0, 0, 0, -1, -1, -1)
time4 = mktime(date4)
# random_time2 = random.uniform(time3, time4)
# t2=asctime(localtime(random_time2))

# t1 = strftime("%Y-%m-%d %H:%M:%S", localtime(random.uniform(time1, time2)))
# t2 = strftime("%Y-%m-%d %H:%M:%S", localtime(random.uniform(time3, time4)))


def createPhone():
    prelist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151", "152", "153",
               "155", "156", "157", "158", "159", "186", "187", "188"]
    return random.choice(prelist) + "".join(random.choice("0123456789") for i in range(8))

users=[]
for i in range(1, 10000):
    # 添加随机人员到时数据库
    user = User()
    user.nick_name = str(i).rjust(5, '0')
    user.password_hash = 'pbkdf2:sha256:50000$lJsx3FLA$46e756412d374e3b9597418e2e04baa899e90ffbf5c0b730cb9868aec6e88d6b'
    user.create_time = strftime("%Y-%m-%d %H:%M:%S", localtime(random.uniform(time1, time2)))
    user.mobile = createPhone()
    user.last_login = strftime("%Y-%m-%d %H:%M:%S", localtime(random.uniform(time3, time4)))
    users.append(user)
    print(i)

with app.app_context():
    db.session.add_all(users)
    db.session.commit()
print('OK')