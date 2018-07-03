function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $(".news_edit").submit(function (e) {
        e.preventDefault()
        // TODO 新闻编辑提交
        $(this).ajaxSubmit({
            beforeSubmit: function (request) {
                // 在提交之前，对参数进行处理

                for (var i = 0; i < request.length; i++) {
                    var item = request[i]
                    if (item["name"] == "content") {
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },

            url: '/admin/news_edit_detail',
            type: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrf_token'),
            },
            success: function (dat) {
                alert(dat.errmsg)
                if (dat.errno == 0) {
                    window.location.href = "/admin/news_edit"
                }

            }

        })


    })


})


// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}