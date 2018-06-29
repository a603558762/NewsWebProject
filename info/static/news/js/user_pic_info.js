function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault()

        //TODO 上传头像
          $(this).ajaxSubmit({
            url: "/profile/pic_info",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (dat) {
                alert(dat.errmsg)
                if (dat.errno == "0") {
                    parent.$('.user_center_pic').children().attr('src',dat.data.user_info.avatar_url)
                    $('.label01').next().attr('src',dat.data.user_info.avatar_url)

                }else {

                }
            }
        })
    })


    })
