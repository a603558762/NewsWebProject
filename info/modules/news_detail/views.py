from flask import render_template, session, current_app, g, request, jsonify, redirect

from info import db
from info.models import User, News, Comment, CommentLike
from info.modules.news_detail import news_blu
from info.utils.common import user_data_info
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
        return jsonify(errno=RET.PARAMERR, errmsg="没有找到新闻")

    # 点击新闻,新闻的点击量+1
    try:
        news.clicks += 1
    except Exception as e:
        current_app.logger.debug(e)

    # 获取新闻评论,2中写法,第二种可以按照时间顺序发给评论排序排序
    news_comments_list = list()
    # for comment in news.comments:
    #     news_comments_list.append(comment.to_dict())
    # print(len(news_comments_list))
    comments = list()
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc())
    except Exception as e:
        current_app.logger.debug(e)
    for comment in comments:
        news_comments_list.append(comment.to_dict())

    # 获取新闻评论的点赞信息  点赞数 每条评论的点赞状态,点赞数

    # 用户没有登录就显示拇指没有被点亮,只显示点赞数

    # 用户登录的话,显示用户的点赞的评论
    user_comment_like_list = list()
    user = g.user
    if user:
        comment_like_count_list = list()
        comment_obj = news.comments
        for temp in comment_obj:
            comment_like_count_list.append(temp.like_count)

        comment_list = list()
        for tem in comments:
            comment_list.append(tem.id)

        comment_likes_obj = None
        try:
            comment_likes_obj = CommentLike.query.filter \
                (CommentLike.user_id == user.id, CommentLike.comment_id.in_(comment_list))

        except Exception as e:
            current_app.logger.debug(e)

        for comment in comment_likes_obj:
            user_comment_like_list.append(comment.comment_id)

    # 新闻排行榜
    rank_top = None
    try:
        rank_top = News.query.order_by(News.clicks.desc()).limit(7)
    except Exception as e:
        current_app.logger.debug(e)
    rank_list = list()

    for i in rank_top:
        rank_list.append(i.to_review_dict())

    # 获取登录状态
    user = g.user
    if not user:
        news_collected = False
    # 文章已收藏
    else:
        if news in user.collection_news:
            news_collected = True
        else:
            news_collected = False

    # 是否已经关注新闻作者

    # if not user:
    isfollowed=False

    if user:
        author = None
        followed = None

        try:
            author_id=news.user_id
            author=User.query.filter(User.id==author_id).first()
            followed=user.followed
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(errno=RET.DATAERR, errmsg="参数错误")

        if author in followed:
            isfollowed=True
        else:
            isfollowed=False

        # followed_list=list()
        # for temp in followed:
        #     followed_list.append(temp.to_dict())

    data = {
        "user": user.to_dict() if user else None,
        "rank_list": rank_list,
        "news_collected": news_collected,
        "news_to_dict": news.to_dict(),
        "news_comments_list": news_comments_list,
        "user_comment_like_list": user_comment_like_list,
        # "followed_list":followed_list,
        "isfollowed":isfollowed

    }

    return render_template('news/detail.html', data=data)


@news_blu.route('/collect_news', methods=['post'])
@user_data_info
def collect_news():
    # 获取用户传过来的数据
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    request_data = request.json
    # print(request_data)
    action = request_data["action"]
    news_id = request_data["news_id"]
    # 新闻id是否存在
    news = None
    try:
        news_id = int(news_id)
        news = News.query.get(news_id)
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(e)

    if not all([action, news]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
    # 收藏命令
    if str(action) == 'collect' and user:
        # 向已经关注的文章中增加文章数据
        try:
            user.collection_news.append(news)
        except Exception as e:
            db.session.rollback()
            current_app.logger.debug(e)
        return jsonify(errno=RET.OK, errmsg="收藏成功")

    # 取消收藏命令
    if str(action) == 'remove' and user:
        try:
            user.collection_news.remove(news)
        except Exception as e:
            current_app.logger.debug(e)
        return jsonify(errno=RET.OK, errmsg="取消收藏成功")


@news_blu.route('/commit', methods=['post'])
@user_data_info
def commit():
    # 判断用户登录状态
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    request_data = request.json
    news_id = request_data.get('news_id')
    comment_from_user = request_data.get('comment')
    parent_comment_id = request_data.get('parent_comment_id')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")
    if not all([comment_from_user, news_id]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误或者新闻不存在")

    # 评论写到数据库中
    comment = Comment()
    try:

        comment.user_id = user.id
        comment.news_id = news_id
        comment.content = comment_from_user
        comment.parent_id = parent_comment_id
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)

    # 将结果返回给前段
    comment_ret = comment.to_dict()
    return jsonify(errno=RET.OK, errmsg="评论成功", comment=comment_ret)


@news_blu.route('/comment_up_down', methods=['post'])
@user_data_info
def comment_up_down():
    user = g.user
    if not user:
        return jsonify(errno=RET.DATAERR, errmsg="请登录!")

    action = request.json.get('action')
    news_id = request.json.get('news_id')
    comment_id = request.json.get('comment_id')

    # 验证参数
    if action not in ['add', 'remove']:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.debug(e)
    news = None
    comment = None
    try:
        news = News.query.get(news_id)
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.debug(e)
    if not news:
        return jsonify(errno=RET.DATAERR, errmsg="新闻不存在")

    # 点赞:
    # if action=='add':
    # 查询是否已经点赞
    # 获取当前新闻的评论
    comment_list = list()
    comment_obj = news.comments
    for temp in comment_obj:
        comment_list.append(temp.id)

    comment_likes_obj = None
    try:
        comment_likes_obj = CommentLike.query.filter \
            (CommentLike.user_id == user.id, CommentLike.comment_id.in_(comment_list))

    except Exception as e:
        current_app.logger.debug(e)

    comment_likes_list = list()
    for commentlike in comment_likes_obj:
        comment_likes_list.append(commentlike.comment_id)
    # 点赞操作
    if action == 'add' and (comment_id not in comment_likes_list):
        try:
            comment_like = CommentLike()
            comment_like.user_id = user.id
            comment_like.comment_id = comment_id
            comment.like_count += 1
            db.session.add(comment_like)
        except Exception as e:
            db.session.rollback()
            current_app.logger.debug(e)
        return jsonify(errno=RET.OK, errmsg="点赞成功")


    # 取消点赞
    elif action == 'remove' and comment_id in comment_likes_list:
        try:
            comment_like = CommentLike.query.filter \
                (CommentLike.user_id == user.id, CommentLike.comment_id == comment_id).first()
            db.session.delete(comment_like)
            comment.like_count -= 1
        except Exception as e:
            db.session.rollback()
            current_app.logger.debug(e)

        return jsonify(errno=RET.OK, errmsg="取消点赞成功")
    else:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")

@news_blu.route('/followed',methods=['post'])
@user_data_info
def followed():
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="请先登录！")
    author_id=request.json.get('author_id')
    action=request.json.get('action')
    if not all([author_id,action]):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    if action not in ['follow','unfollow']:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")

    if action=='follow':

        try:
            author_id=int(author_id)
        except Exception as e:
            current_app.logger.debug(e)
        # 关注作者
        try:
            author=User.query.filter(User.id==author_id).first()
            if author:
                user.followed.append(author)
            else:
                return jsonify(errno=RET.DATAERR, errmsg="没有该作者")
        except Exception as e:
            current_app.logger.debug(e)
        return jsonify(errno=RET.OK, errmsg="关注成功！")
    else:
        try:
            author_id=int(author_id)
        except Exception as e:
            current_app.logger.debug(e)
        # 取消关注作者
        try:
            author=User.query.filter(User.id==author_id).first()
            if author in user.followed:
                try:
                    user.followed.remove(author)
                except Exception as e:
                    current_app.logger.debug(e)
                    return jsonify(errno=RET.DATAERR, errmsg="参数错误")
            else:
                return jsonify(errno=RET.DATAERR, errmsg="没有关注该作者")
        except Exception as e:
            current_app.logger.debug(e)
        return jsonify(errno=RET.OK, errmsg="取消关注成功！")

