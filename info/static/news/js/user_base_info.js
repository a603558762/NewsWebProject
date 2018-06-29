function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}



$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $('input:radio[name="gender"]:checked').val();


        if (!nick_name){
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        var params={signature,nick_name,gender}
        $.ajax({
            url: "/profile/base_info",
            type: "POST",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success: function (dat) {
                if(dat.errno==0){

                    alert(dat.errmsg)}
                    parent.$('.user_center_name').html(dat.data.user_info.nick_name)
                    parent.$('.lgin_pic').next().html(dat.data.user_info.nick_name)
                    // 部分更新

                },error:{

            }
        })


    })
})

function logout(){
    $.ajax({
        url: "/passport/logout",
        type: "get",
        // data: JSON.stringify(params),
        // contentType: "application/json",
        headers: {'X-CSRFToken':getCookie('csrf_token')},
        success: function (dat) {
            location.reload()

            },error:{

        }
    })
}