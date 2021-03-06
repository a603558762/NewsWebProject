import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, g, abort, session, redirect, url_for, jsonify

from info import constants, db
from info.models import User, News, Category
from info.modules.admin import admin_blu
from info.utils.common import user_data_info
from info.utils.image_storage import storage
from info.utils.response_code import RET


@admin_blu.route('/')
@user_data_info
def index():
    user = g.user
    # print(user.nick_name)
    if not user:
        abort(404)
    if not session['is_admin']:
        abort(404)

    data = {
        'user': user.to_dict()
    }
    return render_template('admin/index.html', data=data)


@admin_blu.route('/login', methods=['get', 'post'])
@user_data_info
def login():
    if request.method == 'GET':
        if g.user and session['is_admin']:
            return redirect(url_for('admin.index'))

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
    data = {
        'user': user.to_dict()
    }

    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    # return render_template('admin/index.html', data=data)
    # return redirect('admin/index.html', data=data)
    return redirect(url_for('admin.index'))


@admin_blu.route('/user_count')
def user_count():
    # 总的人数
    users = 0
    month_user = 0
    # day_user = 0
    # 总人数
    try:
        users = User.query.filter(User.is_admin != True).count()

        # 展示数据用:
        # month_user = User.query.filter(User.create_time < '2018-05-15 17:09:31').count()
        # day_user = User.query.filter(User.create_time < '2018-05-28 17:09:31',
        #                              '2018-05-27 17:09:31' < User.create_time).count()

    except Exception as e:
        current_app.logger.debug(e)

    # 月新增人数
    mon_count = 0
    t = time.localtime()
    begin_mon_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 将字符串转成datetime对象
    begin_mon_date = datetime.strptime(begin_mon_date_str, "%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > begin_mon_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    begin_day_date = datetime.strptime(('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day_date).count()
    except Exception as e:
        current_app.logger.error(e)

    if not users:
        return jsonify(errno=RET.DATAERR, errmsg="内部错误")

    active_time = []
    active_count = []

    # 取到今天的时间字符串
    today_date_str = ('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday))
    # 转成时间对象
    today_date = datetime.strptime(today_date_str, "%Y-%m-%d")

    for i in range(0, 31):
        # 取到某一天的0点0分
        begin_date = today_date - timedelta(days=i)
        # 取到下一天的0点0分
        end_date = today_date - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    # User.query.filter(User.is_admin == False, User.last_login >= 今天0点0分, User.last_login < 今天24点).count()

    # 反转，让最近的一天显示在最后
    active_time.reverse()
    active_count.reverse()

    data = {
        'user_total': users,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_time': active_time,
        'active_count': active_count

    }

    return render_template('admin/user_count.html', data=data)


@admin_blu.route('/user_list')
def user_list():
    current_page = request.args.get('page', 1)

    try:
        current_page = int(current_page)
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    # 查询所有用户,分页
    user_paginate = None
    try:
        user_paginate = User.query.filter(User.is_admin != True).paginate \
            (page=current_page, per_page=constants.ADMIN_USER_PAGE_MAX_COUNT, error_out=False)
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据查询错误")
    if not user_paginate:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
    total_page = user_paginate.pages
    current_page = user_paginate.page
    user_per_list = list()
    for temp in user_paginate.items:
        user_per_list.append(temp.to_admin_dict())
    data = {
        'total_page': total_page,
        'current_page': current_page,
        'user_per_list': user_per_list
    }

    return render_template('admin/user_list.html', data=data)


@admin_blu.route('/news_review', methods=['get', 'post'])
def news_review():
    keywords = request.form.get('keywords', '')
    if request.method != "POST" or (request.method == 'POST' and keywords == ''):
        current_page = request.args.get('page', 1)
        try:
            current_page = int(current_page)
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(errno=RET.DATAERR, errmsg="参数错误")

        news_paginate = News.query.order_by(News.create_time.desc()).paginate \
            (page=current_page, per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT)

        total_page = news_paginate.pages
        current_page = news_paginate.page
        news_list = list()

        for temp in news_paginate.items:
            news_list.append(temp.to_review_dict())

        data = {
            'news_list': news_list,
            'total_page': total_page,
            'current_page': current_page
        }
        return render_template('admin/news_review.html', data=data)
    news = None
    try:
        news = News.query.filter(News.title.contains(keywords)).all()
    except Exception as e:
        current_app.logger.debug(e)
    news_list = list()
    if not news:
        return jsonify(errno=RET.DATAERR, errmsg="没有查到")
    for temp in news:
        news_list.append(temp.to_review_dict())

    data = {
        'news_list': news_list
    }
    return render_template('admin/news_review.html', data=data)


@admin_blu.route('/news_edit', methods=['get', 'post'])
def news_edit():
    # 查询新闻
    keywords = request.form.get('keywords', '')
    if request.method != "POST" or (request.method == 'POST' and keywords == ''):
        current_page = request.args.get('page', 1)
        try:
            current_page = int(current_page)
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(errno=RET.DATAERR, errmsg="参数错误")

        news_paginate = News.query.order_by(News.create_time.desc()).paginate \
            (page=current_page, per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT)

        total_page = news_paginate.pages
        current_page = news_paginate.page
        news_list = list()

        for temp in news_paginate.items:
            news_list.append(temp.to_review_dict())

        data = {
            'news_list': news_list,
            'total_page': total_page,
            'current_page': current_page
        }
        return render_template('admin/news_edit.html', data=data)
    news = None
    try:
        news = News.query.filter(News.title.contains(keywords)).all()
    except Exception as e:
        current_app.logger.debug(e)
    news_list = list()
    if not news:
        return jsonify(errno=RET.DATAERR, errmsg="没有查到")
    for temp in news:
        news_list.append(temp.to_review_dict())

    data = {
        'news_list': news_list
    }
    # return render_template('admin/news_review.html', data=data)

    return render_template('admin/news_edit.html', data=data)


@admin_blu.route('/news_type', methods=['get', 'post'])
def news_type():
    # 查询分类
    if request.method == "GET":
        categories = None
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.debug(e)
        if not categories:
            return jsonify(errno=RET.DATAERR, errmsg="参数查询错误")
        data = {
            'category': categories
        }
        return render_template('admin/news_type.html', data=data)
    else:
        c_id=request.json.get('id')
        c_name=request.json.get('name',0)

        # if not c_name:
        #     return jsonify(errno=RET.DATAERR, errmsg="参数错误")
        if c_id:

            try:
                c_id=int(c_id)
            except Exception as e:
                current_app.logger.debug(e)
                return jsonify(errno=RET.DATAERR, errmsg="参数错误")

            category=None
            try:
                # category = Category.query.get(c_id)
                category = Category.query.filter(Category.id==c_id).first()
            except Exception as e:
                current_app.logger.debug(e)
                return jsonify(errno=RET.DATAERR, errmsg="参数错误或者分类不存在")
            if not category:
                return jsonify(errno=RET.DATAERR, errmsg="查询错误")

            try:
                category.name=c_name
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.debug(e)
                return jsonify(errno=RET.DATAERR, errmsg="内部错误")
            return jsonify(errno=RET.OK, errmsg="修改成功")

        if not c_name:
            return jsonify(errno=RET.DATAERR, errmsg="分类名称不能为空")
        try:
            category=Category()
            category.name=c_name
            db.session.add(category)
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(errno=RET.DATAERR, errmsg="内部错误")
        return jsonify(errno=RET.OK, errmsg="保存成功")


@admin_blu.route('/news_review_detail', methods=['get', 'post'])
def news_review_detail():
    if request.method == "GET":
        news_id = request.args.get('news_id')
        if not news_id:
            return jsonify(errno=RET.DATAERR, errmsg="参数错误")
        try:
            news = News.query.filter(News.id == news_id).first()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
        if not news:
            return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")

        # 查询所有的分类,在前段渲染本身的分类:
        categories = None
        category_list = list()
        try:
            categories = Category.query.all()

        except Exception as e:
            current_app.logger.debug(e)
        categories.pop(0)
        for temp in categories:
            category_list.append(temp.to_dict())

        data = {
            'news': news.to_dict(),
            'category_list': category_list

        }
        return render_template('admin/news_review_detail.html', data=data)

    title = request.form.get('title')
    # pic = request.files.get('index_image')
    news_id = request.form.get('news_id')
    content = request.form.get('content')
    digest = request.form.get('digest')
    category = request.form.get('category_id')
    action = request.form.get('action')
    reason = request.form.get('reason', '')

    iscategory = None
    try:
        iscategory = Category.query.filter(Category.id == category)
    except Exception as e:
        current_app.logger.debug(e)

    if not all([title, content, digest, category, news_id]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")

    # 非空校验
    if not iscategory:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    if action not in ['accept', 'reject']:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    news = None
    try:
        news = News.query.filter(News.id == news_id).first()
    except Exception as e:
        current_app.logger.debug(e)
    if not news:
        return jsonify(errno=RET.DATAERR, errmsg="新闻不存在")

    try:
        news.status = 0 if action == 'accept' else -1
        news.reason = reason
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(e)

    return jsonify(errno=RET.OK, errmsg="OK")

    # 上传用户图片
    # pic_url = None
    # try:
    #     pic_url = constants.QINIU_DOMIN_PREFIX + storage(pic.read())
    #     print(pic_url)
    # except Exception as e:
    #     current_app.logger.debug(e)
    # try:
    #     news = News()
    #     news.user_id = user.id
    #     news.category_id = category
    #     news.digest = digest
    #     news.source = user.nick_name
    #     news.content = content
    #     news.title = title
    #     news.status = 1
    #     news.index_image_url = pic_url
    #     db.session.add(news)
    #     db.session.commit()
    #
    # except Exception as e:
    #     current_app.logger.debug(e)


@admin_blu.route('/news_edit_detail', methods=['get', 'post'])
def news_edit_detail():
    if request.method == "GET":
        news_id = request.args.get('news_id')
        if not news_id:
            return jsonify(errno=RET.DATAERR, errmsg="参数错误")
        try:
            news = News.query.filter(News.id == news_id).first()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
        if not news:
            return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")

        # 查询所有的分类,在前段渲染本身的分类:
        categories = None
        category_list = list()
        try:
            categories = Category.query.all()

        except Exception as e:
            current_app.logger.debug(e)
        categories.pop(0)
        for temp in categories:
            category_list.append(temp.to_dict())

        data = {
            'news': news.to_dict(),
            'category_list': category_list

        }
        return render_template('admin/news_edit_detail.html', data=data)

    title = request.form.get('title')
    # pic = request.files.get('index_image')
    news_id = request.form.get('news_id')
    content = request.form.get('content')
    digest = request.form.get('digest')
    category = request.form.get('category_id')
    # action = request.form.get('action')
    # reason = request.form.get('reason', '')
    pic = request.files.get('pic')

    iscategory = None
    try:
        iscategory = Category.query.filter(Category.id == category)
    except Exception as e:
        current_app.logger.debug(e)

    if not all([title, content, digest, category, news_id]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")

    # 非空校验
    if not iscategory:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    # if action not in ['accept', 'reject']:
    #     return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    news = None
    try:
        news = News.query.filter(News.id == news_id).first()
    except Exception as e:
        current_app.logger.debug(e)
    if not news:
        return jsonify(errno=RET.DATAERR, errmsg="新闻不存在")

    # try:
    # news.status = 0 if action == 'accept' else -1
    # news.reason = reason
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.debug(e)

    # 上传用户图片
    pic_url = None
    if pic:
        try:
            pic_url = constants.QINIU_DOMIN_PREFIX + storage(pic.read())
            print(pic_url)
        except Exception as e:
            current_app.logger.debug(e)
    try:
        # news = News()
        # news.user_id = user.id
        news.category_id = category
        news.digest = digest
        # news.source = user.nick_name
        news.content = content
        news.title = title
        # news.status = 1
        if pic_url:
            news.index_image_url = pic_url
        # db.session.add(news)
        db.session.commit()

    except Exception as e:
        current_app.logger.debug(e)

    # return render_template('admin/news_edit_detail.html')
    return jsonify(errno=RET.OK, errmsg="OK")

# @admin_blu.route('/news_category')
# def news_category():
#     return render_template('')
