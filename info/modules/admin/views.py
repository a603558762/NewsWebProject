from flask import render_template, request, current_app

from info.models import User
from info.modules.admin import admin_blu


@admin_blu.route('/')
def index():
    return render_template('admin/index.html')


@admin_blu.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'GET':
        data = {
            'error': ''
        }
        return render_template('admin/login.html', data=data)

    mobile = request.form.get('username')
    password = request.form.get('password')
    if not all([mobile, password]):
        data = {
            'error': '用户名或者密码不能为空'
        }
        return render_template('admin/login.html', data=data)
    # 检查用户名和密码
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.debug(e)
        data = {
            'error': '内部错误'
        }
        return render_template('admin/login.html', data=data)
    if not user:
        data = {
            'error': '用户名不存在'
        }
        return render_template('admin/login.html', data=data)
    # 校验密码:
    is_password = False
    try:
        is_password = user.check_passowrd(password)
    except Exception as e:
        current_app.logger.debug(e)
        data = {
            'error': '内部错误'
        }
        return render_template('admin/login.html', data=data)
    if not is_password:
        data = {
            'error': '密码错误'
        }
        return render_template('admin/login.html', data=data)
    data={
        'user':user.to_dict()
    }

    return render_template('admin/index.html',data=data)
