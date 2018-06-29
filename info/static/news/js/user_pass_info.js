function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();
        var password_old=$("input[name='password_old']").val();
        var password_new=$("input[name='password_new']").val();
        var password_new2=$("input[name='password_new2']").val();

        if(!password_old || !password_new || !password_new2){alert('密码不能为空')}
        if(password_new!=password_new2){
            alert('两次输入不一致')
            return
        }
        // TODO 修改密码
        params={
            password_old,password_new
        }
        $.ajax({
            url: "/profile/pass_info",
            type: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success: function (dat) {

                if(dat.errno==4106){alert('密码错误!')}
                else if(dat.errno==0){alert('修改成功!')}
                },error:{

            }
        })
    })
})