from flask import render_template, request, current_app, g, abort, session

from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_data_info


@admin_blu.route('/')
@user_data_info
def index():
    user=g.user
    if not user :
        abort(404)
    if not session['is_admin']:
        abort(404)

    data={
        'user':user.to_dict()
    }
    return render_template('admin/index.html',data=data)


@admin_blu.route('/login', methods=['get', 'post'])
@user_data_info
def login():
    if request.method == 'GET':
        if g.user and session['is_admin']:
            data = {
                'user': g.user.to_dict()
            }
            return render_template('admin/index.html', data=data)

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
