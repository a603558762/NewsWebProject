function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    })

    // 收藏
    $(".collection").click(function () {
        var action="collect";
        var news_id=$(this).attr('news_id');

        params={
           "action" :action,
            "news_id":news_id
        }
        $.ajax({
            url: "/news_detail/collect_news",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",

            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success: function (dat) {


                if(dat.errno==0){

                    $('.collection').hide()
                    $(".collected").show()
                }

                },error:{

            }
        })


    })

    // 取消收藏
    $(".collected").click(function () {
        var action="remove";
        var news_id=$(this).attr('news_id');

        params={
           "action" :action,
            "news_id":news_id
        }
        $.ajax({
            url: "/news_detail/collect_news",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",

            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success: function (dat) {


                if(dat.errno==0){


                    $(".collected").hide()
                    $('.collection').show()
                }

                },error:{

            }
        })
     
    })

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        // 获取会的福评论的comment_id

        var comment=$('.comment_input').val();
        var news_id=$('.comment_input').attr('news_id')

        // 提交评论

        params ={
            comment,
            news_id
        }

        $.ajax({
            url: "/news_detail/commit",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success: function (dat) {
                console.log(dat.comment)
                if (dat.errno==0){
                // 拼接评论

                var content='<div class="comment_list">' +
                    '<div class="person_pic fl">' +
                    '<img src="../../static/news/images/worm.jpg" alt="用户图标"></div>' +
                    '<div class="user_name fl">'+dat.comment.user.nick_name+'</div>' +
                    '<div class="comment_text fl" comment_id="'+dat.comment.id+'">'+dat.comment.content+'</div>' +
                    '<div class="comment_time fl">'+dat.comment.create_time+'</div>' +
                    '                <a href="javascript:;" class="comment_up fr">赞</a>' +
                    '                <a href="javascript:;" class="comment_reply fr">回复</a>' +
                    '                <from class="reply_form fl"  comment_id="'+ dat.comment.id +'" news_id="'+dat.comment.news_id +'">' +
                    '                    <textarea  class="reply_input"></textarea>' +
                    '                    <input type="submit" name="" value="回复" class="reply_sub fr">' +
                    '                    <input type="reset" name="" value="取消" class="reply_cancel fr">' +
                    '                </from>' +
                    '</div>'

                $('.comment_list_con').prepend(content)

                updateCommentCount()

                        // 请空输入框
                // $(this).prev().val('')

                }
                } ,error:{

            }
        })



    })

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);

            var count=Number($(this).text())
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
                count-=1
                $(this).text(count)

                // 取消点赞

                var params={
                    action:'remove',
                    news_id:$('.comment_input').attr('news_id'),
                    comment_id:$this.attr('comment_id')
                }
                $.ajax({
                    url: "/news_detail/comment_up_down",
                    type: "post",
                    data: JSON.stringify(params),
                    contentType: "application/json",
                    headers: {'X-CSRFToken':getCookie('csrf_token')},
                    success: function (dat) {
                        // if (dat.errno!=0){
                        //     alert(dat.errmsg)
                        // }

                        },error:{

                    }
                })



            }else {
                count+=1
                $(this).text(count)

                $this.addClass('has_comment_up')
           // 点赞加1

                // 点赞
                var params={
                    action:'add',
                    news_id:$('.comment_input').attr('news_id'),
                    comment_id:$this.attr('comment_id')
                }
                $.ajax({
                    url: "/news_detail/comment_up_down",
                    type: "post",
                    data: JSON.stringify(params),
                    contentType: "application/json",
                    headers: {'X-CSRFToken':getCookie('csrf_token')},
                    success: function (dat) {
                        if (dat.errno!=0){

                        }

                        },error:{

                    }
                })



            }
        }

        if(sHandler.indexOf('reply_sub')>=0)

        {  // 获取得到新闻的id , 评论的内容 , 回复的评论的id
         var parent_comment_id=$(this).parent().attr('comment_id');
         var news_id=$(this).parent().attr('news_id');
         var comment=$(this).prev().val();

         if(!comment){alert('评论不能为空')};
            params={
             parent_comment_id,news_id,comment
            }

            $.ajax({
                url: "/news_detail/commit",
                type: "post",
                data: JSON.stringify(params),
                contentType: "application/json",
                headers: {'X-CSRFToken':getCookie('csrf_token')},
                success: function (dat) {
                    var content='<div class="comment_list">' +
                        '                <div class="person_pic fl">' +
                        '                    <img src="../../static/news/images/worm.jpg" alt="用户图标">' +
                        '                </div>' +
                        '                <div class="user_name fl">'+dat.comment.user.nick_name+'</div>' +
                        '                <div class="comment_text fl">'+dat.comment.content+'</div>' +
                        '                <div class="reply_text_con fl">' +
                        '                    <div class="user_name2">'+dat.comment.parent.user.nick_name+'</div>' +
                        '                    <div class="reply_text">'+dat.comment.parent.content+'</div>' +
                        '                </div>' +
                        '                <div class="comment_time fl">'+dat.comment.create_time+'</div>' +
                        '                <a href="javascript:;" class="comment_up has_comment_up fr">1</a>' +
                        '                <a href="javascript:;" class="comment_reply fr">回复</a>' +
                        '                <from class="reply_form fl" comment_id="'+ dat.comment.id +'" news_id="'+dat.comment.news_id +'" >' +
                        '                    <textarea  class="reply_input"></textarea>' +
                        '                    <input type="submit" name="" value="回复" class="reply_sub fr">' +
                        '                    <input type="reset" name="" value="取消" class="reply_cancel fr">' +
                        '                </from>' +
                        '            </div>'


                $(".comment_list_con").prepend(content);
                    //   TODO 评论数加1
                updateCommentCount()
                // 请空输入框
                // $this.prev().val('')
                        // 关闭
                    },error:{

                }
            })

        }
    })

        // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})

function updateCommentCount() {
    var count = $(".comment_list").length
    $(".comment_count").html(count+"条评论")
}