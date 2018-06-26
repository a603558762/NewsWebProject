import logging

from flask import session, render_template, current_app, request, jsonify

# from info import redis_store
from info.models import User, News, Category
from info.utils.response_code import RET
from . import Index_blu
from info import redis_store

@Index_blu.route('/')
def index():
    redis_store.set('name','hao')
    # 使用session设置sid的session是从from flask import session导入的
    # 设置session位置保存的时候使用的是:TODO from flask_session import Session
    # 通过浏览器的cookie来判断是不是已经登录的用户


    # 排行榜,首先获取数据
    rank_top=None
    try:
        rank_top=News.query.order_by(News.clicks.desc()).limit(7)
    except Exception as e:
        current_app.logger.debug(e)
    rank_list=list()

    for i in rank_top:
        rank_list.append(i.title)
    # 获取category分类信息:
    category=None
    category_list=list()
    try:
        category=Category.query.all()
    except Exception as e:
        current_app.logger.debug(e)
    for i in category:
        category_list.append(i.to_dict())






    # 获取登录状态
    nick_name=session.get("nick_name",None)
    user = None
    try:
        user=User.query.filter(User.nick_name==nick_name).first()
    except Exception as e:
        current_app.logger.debug(e)


    data={
        "user":user.to_dict() if user else None,
        "rank_list":rank_list,
        "category_list":category_list
    }
    print(data["category_list"])




    return render_template('news/index.html',data=data)


@Index_blu.route('/news_list')
def news_list():
    # 获取请求的新闻
    # print(request.args)
    cid=request.args.get('currentCid','1')
    cur_page=request.args.get('cur_page','1')
    per_page = request.args.get("per_page",'5')

    """ImmutableMultiDict([('{"currentCid":0,"cur_page":1}', '')])"""

    # print(cid)
    # print(cur_page)
    # 校验数据
    try:
        cid=int(cid)
        cur_page=int(cur_page)
        per_page=int(per_page)
    except Exception as e:
        current_app.logger.debug(e)



    # 获取最新的文章的信息
    # cid为1 的时候,category表里有,但是在News表单里面没有cid为1的
    pagination=None
    query_info=[]
    if cid!=1:
        query_info.append(News.category_id==cid)


    try:
        pagination=News.query.filter(*query_info).order_by(News.create_time.desc()).paginate(page=cur_page, per_page=per_page, error_out=False)
    except Exception as e:
        current_app.logger.debug(e)
    if not pagination:
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    # 总页数
    totale_pages=pagination.pages
    # 当前返回的页码
    current_page = pagination.page

    news_list_dict=[]
    for i in pagination.items:
        news_list_dict.append(i.to_basic_dict())

    data={
        "news_list_dict":news_list_dict,
        "total_pages":totale_pages,
        "current_page":current_page
    }
    print('Newslist数据传输成功')
    print('totale_pages:',totale_pages)
    return jsonify(errno=RET.OK, errmsg="OK",data=data)



@Index_blu.route('/favicon.ico')
def favicon():
    # 固定写法,每个网站都是固定的写法有这个favicon.ico
    return current_app.send_static_file('news/favicon.ico')