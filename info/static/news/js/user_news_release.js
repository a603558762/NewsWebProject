function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault()

        // TODO 发布完毕之后需要选中我的发布新闻

        $(this).ajaxSubmit({
            url: "/profile/user_news_release",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function(dat){
                if(dat.errno==0){
                alert(dat.errmsg)
                window.location.href='/profile/user_news_list'
                }
            }
        })



    })
})