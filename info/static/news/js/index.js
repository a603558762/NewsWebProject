var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')
        // console.log($(this))
        // console.log(currentCid)

        currentCid = clickCid
        cur_page = 1
        total_page = 1
        updateNewsData()
        // if (clickCid != currentCid) {
        //     // 记录当前分类id
        //     currentCid = clickCid
        //
        //     // 重置分页参数
        //     cur_page = 1
        //     total_page = 1
        //
        //
        //     updateNewsData()
        // }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();
        // console.log(showHeight,pageHeight)
        if ((canScrollHeight - nowScroll) < 100) {
            if(cur_page<total_page){
            // TODO 判断页数，去更新新闻数据
            cur_page+=1
            updateNewsData()
            }else{
                // 到底了
            }
        }
    })
})
updateNewsData()
function updateNewsData() {
    // TODO 更新新闻数据
    var params={
        "currentCid": currentCid,
        "cur_page":cur_page,
        "total_page":total_page
    }
    // console.log(params)

    $.get('/news_list',params,function (dat) {
        // get
        // console.log(dat.data)
        // 当访问的是首页的时候
        if(cur_page==1) {
            // 首页的新闻列表清空
            $('.list_con').html("")
        }
        total_page=dat.data.total_pages
        // console.log(dat.data)


            var content=''
            for(i=0;i<dat.data.news_list_dict.length;i++){
                    // console.log(dat.data)

                  content+='<li>'
                            +'<a href="#" class="news_pic fl"><img src="'+dat.data.news_list_dict[i].index_image_url+'"></a>'
                            +'<a href="#" class="news_title fl">'+dat.data.news_list_dict[i].title+'</a>'
                            +'<a href="#" class="news_detail fl">'+dat.data.news_list_dict[i].digest+'</a>'
                            +'<div class="author_info fl">'
                                +'<div class="author fl">'
                                    +'<img src="../../static/news/images/person.png" alt="author">'
                                    +'<a href="#">'+dat.data.news_list_dict[i].source+'</a>'
                                +'</div>'
                                +'<div class="time fl">'+dat.data.news_list_dict[i].create_time+'</div>'
                            +'</div>'
                        +'</li>'
            }
            // console.log(content)
            $('.list_con').append(content)





            // 加载传回来的新闻消息
        // }
    })
}


