from datetime import datetime

from flask import render_template, redirect, url_for, request, jsonify, current_app, g

from info import db, constants
from info.models import Category, News
from info.modules.profile import profile_blu
from info.utils.common import user_data_info
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route('/')
@user_data_info
def center():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    user_info = user.to_dict()
    data = {
        'user': user_info,
    }

    return render_template('news/user.html', data=data)


@profile_blu.route('/base_info', methods=['get', 'post'])
@user_data_info
def base_info():
    print(request.json)
    if request.method != 'POST':
        return render_template('news/user_base_info.html')

    signature = request.json.get('signature')
    nick_name = request.json.get('nick_name')
    gender = request.json.get('gender')
    user = g.user
    # 验证参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")

    if not user:
        return jsonify(errno=RET.DATAERR, errmsg="没有登录!")
    try:
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(e)
    data = {

        'user_info': user.to_dict()
    }

    return jsonify(errno=RET.OK, errmsg="更新成功!", data=data)


@profile_blu.route('/pic_info', methods=['get', 'post'])
@user_data_info
def pic_info():
    user = g.user

    if request.method != 'POST':
        data = {
            'user_info': user.to_dict()

        }

        return render_template('news/user_pic_info.html', data=data)

    file = request.files.get('avatar').read()
    # 判断图片是否为空
    if not file:
        return jsonify(errno=RET.DATAERR, errmsg="请选择图片")

    key = storage(file)

    try:
        user.avatar_url = key
    except Exception as e:
        current_app.loger.debug(e)
    user_info = user.to_dict()
    data = {
        'user_info': user_info
    }
    return jsonify(errno=RET.OK, errmsg="上传成功!", data=data)


@profile_blu.route('/follow')
def follow():
    return render_template('news/user_follow.html')


@profile_blu.route('/pass_info', methods=['get', 'post'])
@user_data_info
def pass_info():
    user = g.user
    if request.method != 'POST':
        return render_template('news/user_pass_info.html')
    password_old = request.json.get('password_old')
    password_new = request.json.get('password_new')
    # 验证旧密码
    ispassword = False
    try:
        ispassword = user.check_passowrd(password_old)
    except Exception as e:
        current_app.logger.debug(e)
    if not ispassword:
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")
    # 重新写密码
    try:
        user.password = password_new
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)

    return jsonify(errno=RET.OK, errmsg="修改成功")


@profile_blu.route('/user_collection', methods=['post', 'get'])
@user_data_info
def user_collection():
    # if request.method!='POST':
    current_page = request.args.get('current_page', 1)
    try:
        current_page = int(current_page)
    except Exception as e:
        current_page.logger.debug(e)
    user = g.user

    collect_news = user.collection_news.paginate(page=current_page, per_page=constants.USER_COLLECTION_MAX_NEWS,
                                                 error_out=False)
    total_page = collect_news.pages
    current_page = collect_news.page
    collect_news_li = collect_news.items
    collect_news_list = list()
    for news in collect_news_li:
        collect_news_list.append(news.to_review_dict())

    data = {
        'collect_news_list': collect_news_list,
        'total_page': total_page,
        'current_page': current_page,
    }
    # return jsonify(errno=RET.OK, errmsg="发布成功!",data=data)
    return render_template('news/user_collection.html',data=data)


@profile_blu.route('/user_news_release', methods=['get', 'post'])
@user_data_info
def user_news_release():
    user = g.user
    if request.method != 'POST':
        category = None
        try:
            category = Category.query.all()
        except Exception as e:
            current_app.logger.debug(e)
        if not category:
            return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
        category_list = list()
        category.pop(0)
        for temp in category:
            category_list.append(temp.to_dict())
        data = {
            'category_list': category_list
        }
        return render_template('news/user_news_release.html', data=data)

    title = request.form.get('title')
    pic = request.files.get('index_image')

    content = request.form.get('content')
    digest = request.form.get('digest')
    category = request.form.get('category_id')

    iscategory = None
    try:
        iscategory = Category.query.filter(Category.id == category)
    except Exception as e:
        current_app.logger.debug(e)

    if not all([title, pic, content, digest, category]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")

    # 非空校验
    if not iscategory:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    # 上传用户图片
    pic_url = None
    try:
        pic_url = constants.QINIU_DOMIN_PREFIX + storage(pic.read())
        print(pic_url)
    except Exception as e:
        current_app.logger.debug(e)
    try:
        news = News()
        news.user_id = user.id
        news.category_id = category
        news.digest = digest
        news.source = user.nick_name
        news.content = content
        news.title = title
        news.status = 0
        news.index_image_url = pic_url
        db.session.add(news)
        db.session.commit()

    except Exception as e:
        current_app.logger.debug(e)

    return jsonify(errno=RET.OK, errmsg="OK")


@profile_blu.route('/user_news_list')
@user_data_info
def user_news_list():
    user = g.user
    # 查询新闻分类
    current_page=request.args.get('current_page',1)
    try:
        current_page=int(current_page)
    except Exception as e:
        current_app.logger.debug(e)

    user_news=user.news_list.paginate(page=current_page,per_page=constants.OTHER_NEWS_PAGE_MAX_COUNT, error_out=False)
    total_page=user_news.pages
    current_page=user_news.page
    user_news_list=list()
    for temp in user_news.items:
        user_news_list.append(temp.to_review_dict())

    data={
        'user_news_list':user_news_list,
        'total_page':total_page,
        'current_page':current_page
    }
    return render_template('news/user_news_list.html',data=data)
