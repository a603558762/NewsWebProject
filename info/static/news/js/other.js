// 解析url中的查询字符串
function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(function () {
    // 页面加载完毕，获取新闻列表
    getNewsList(1)

    // TODO 关注当前作者
    $(".focus").click(function () {


        var author_id = $(".user_menu_con").attr('author_id')
        var action = 'follow'
        // var $user=$(this).parent()
        // var count=$user.children('div.follows').find('b').text()
        // count=Number(count)
        params = {
            author_id, action
        }
        $.ajax({
            url: "/profile/other",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken': getCookie('csrf_token')},

            success: function (dat) {
                alert(dat.errmsg)
                if (dat.errno == 0) {
                    $('.focus').hide()
                    $('.focused').show()
                }

            }, error: {}
        })


    })

    // TODO 取消关注当前作者


    $(".focused").click(function () {

        var author_id = $(".user_menu_con").attr('author_id')
        var action = 'unfollow'
        // var $user=$(this).parent()
        // var count=$user.children('div.follows').find('b').text()
        // count=Number(count)
        params = {
            author_id, action
        }
        $.ajax({
            url: "/profile/other",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken': getCookie('csrf_token')},

            success: function (dat) {
                alert(dat.errmsg)
                if (dat.errno == 0) {
                    $('.focused').hide()
                    $('.focus').show()
                }

            }, error: {}
        })


    })
})

// TODO 获取新闻列表
function getNewsList(page) {


}
