function ShowLargeImage(imgsrc){
    $('#main_image').attr('src',imgsrc);
}
function fillpage(page){
    console.log('Page selected',page)
    $('#page').val(page);
    $('#filter_form').submit();
}
function AddProductToBasket(productid){
    const product_count = $('#product_count').val();
    $.get('/add-to-order?product_id=' + productid + '&count=' + product_count).then(res=>{
        Swal.fire({
                    title: "message",
                    text: res.text,  
                    icon: res.icon,
                    showCancelButton: false,
                    confirmButtonColor: "#ea290fff",
                    confirmButtonText: res.confirmButtonText    
        }).then(result =>{
            if (res.status === 'not log in'){
               window.location.href = "/login/";
            }
        });
    });
}

function changeOrderDetailCount(detailId, state) {
    $.get('/user/change-order-detail?detail_id=' + detailId + '&state=' + state).then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body);
        }
    });
}
function ToggleLike(productId, el) {
    $.post({
        url: '/like/' + productId + '/',
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        },
        success: function (res) {
            const icon = $(el).find('i');  // ← اینجا اصلاح شد

            if (res.liked) {
                icon.removeClass('fa-heart-o').addClass('fa-heart heart-red');
            } else {
                icon.removeClass('fa-heart heart-red').addClass('fa-heart-o');
            }

            if (res.status === 'not log in') {
                window.location.href = "/login/";
            }
        }
    });
}
