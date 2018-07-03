function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".focused").click(function () {
        // TODO 取消关注当前新闻作者

        var author_id = $(this).parent().attr('author_id')
        var action = 'unfollow'
        var $user=$(this).parent()
        var count=$user.children('div.follows').find('b').text()
        count=Number(count)

        params = {
            author_id, action
        }
        $.ajax({
            url: "/profile/follow",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken': getCookie('csrf_token')},

            success: function (dat) {
                alert(dat.errmsg)
                if (dat.errno == 0) {

                    $user.children('a.focus').show()
                    $user.children('a.focused').hide()
                    count-=1
                    $user.children('div.follows').find('b').html(count)

                    // $user.hide()
                    // $(this).prev().show()
                    // $('.focus').show()
                    // $('.focused').hide()
                    // count -= 1
                    // $('div.follows > b').html(count)
                }

            }, error: {}
        })

    })


    $(".focus").click(function () {
        var author_id = $(this).parent().attr('author_id')
        var action = 'follow'
        var $user=$(this).parent()
        var count=$user.children('div.follows').find('b').text()
        count=Number(count)

        // count = $('div.follows > b').text()
        // count = Number(count)
        params = {
            author_id, action
        }
        $.ajax({
            url: "/profile/follow",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken': getCookie('csrf_token')},

            success: function (dat) {
                alert(dat.errmsg)
                if (dat.errno == 0) {
                    $user.children('a.focus').hide()
                    $user.children('a.focused').show()
                    count += 1
                    $user.children('div.follows').find('b').html(count)

                }

            }, error: {}
        })

    })


})
