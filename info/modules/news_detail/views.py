from flask import render_template, session, current_app, g, request, jsonify

from info.models import User, News
from info.modules.news_detail import news_blu
from info.utils.common import  user_data_info
from info.utils.response_code import RET


@news_blu.route('/<int:news_id>')
@user_data_info
def news_detail(news_id):
    # 获取新闻是否存在
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.debug(e)

    if not news:
        return '没有找到新闻!'


    # 新闻排行榜
    rank_top = None
    try:
        rank_top = News.query.order_by(News.clicks.desc()).limit(7)
    except Exception as e:
        current_app.logger.debug(e)
    rank_list = list()

    for i in rank_top:
        rank_list.append(i.title)

    # 获取登录状态
    user=g.user
    if not user:
        news_collected=False
   # 文章已收藏

    else:
        if news in user.collection_news:
            news_collected=True
        else:
            news_collected=False

    # print('新闻标题:',news.title)

    data = {
        "user": user.to_dict() if user else None,
        "rank_list": rank_list,
        "news_collected":news_collected,
        "news_to_dict":news.to_dict()
    }
    # print(news.to_dict())
    return render_template('/news/detail.html',data=data)


@news_blu.route('/collect_news',methods=['post'])
@user_data_info
def collect_news():
    # 获取用户传过来的数据
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    request_data=request.json
    # print(request_data)
    action=request_data["action"]
    news_id=request_data["news_id"]
    # 新闻id是否存在
    news=None
    try:
        news_id=int(news_id)
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.debug(e)


    if not all([action,news]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
    # 收藏命令
    if str(action)=='collect' and user:
        # 向已经关注的文章中增加文章数据
        try:
            user.collection_news.append(news)
        except Exception as e:
            current_app.logger.debug(e)
        print('关注成功')
        return jsonify(errno=RET.OK, errmsg="收藏成功")



    # 取消收藏命令
    if str(action) == 'remove' and user:
        try:
            user.collection_news.remove(news)
        except Exception as e:
            current_app.logger.debug(e)
        print('取消收藏成功')
        return jsonify(errno=RET.OK, errmsg="取消收藏成功")




