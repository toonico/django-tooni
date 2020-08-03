 $(document).ready(function ($) {
                $("#check_module").click(function (e) {
                var IMP = window.IMP; // 생략가능
                var type = $('.charge-type input:checked').val();
                var amount_id =$('#result').val();
                var my_proname = $('#pro_name').val();
                var merchant = $('#merchant_id');
                amount_id = amount_id*1;
                var merchant_id = AjaxStoreTransaction(e, amount_id, type);
                IMP.init('imp59252354');
                //console.log(merchant);
                console.log(amount_id);
                console.log(my_proname);
                console.log(merchant_id);
                IMP.request_pay({
                pg: 'danal', // version 1.1.0부터 지원.
                pay_method: type,
                merchant_uid: merchant_id,
                name: my_proname,
                amount : amount_id,
                buyer_email: 'iamport@siot.do',
                buyer_name: $('#user_name').val(),
                buyer_tel: '010-1234-5678',
                buyer_addr: '서울특별시 강남구 삼성동',
                buyer_postcode: '123-456',
                m_redirect_url: 'https://www.yourdomain.com/payments/complete'
                }, function (rsp) {
                console.log(rsp);
                if (rsp.success) {
                var msg = '결제가 완료되었습니다.';
                msg += '고유ID : ' + rsp.imp_uid;
                msg += '상점 거래ID : ' + rsp.merchant_uid;
                msg += '결제 금액 : ' + rsp.paid_amount;
                msg += '카드 승인번호 : ' + rsp.apply_num;
                console.log(rsp.merchant_uid);
                console.log(rsp.imp_uid);
                console.log(rsp.paid_amount);
                ImpTransaction(e, rsp.merchant_uid, rsp.imp_uid, rsp.paid_amount,rsp.status);
                } else {
                var msg = '결제에 실패하였습니다.';
                msg += '에러내용 : ' + rsp.error_msg;
                }
                alert(msg);
                });
            });

 function AjaxStoreTransaction(e, amount_id, type_id) {
            e.preventDefault();
            var merchant_id = '';
            var form = $('#paymentform')[0];
            var formData = new FormData(form);
            formData.append('amount_id', amount_id);
            formData.append('type_id', type_id);

            var request = $.ajax({
                processData: false,
                contentType: false,
                type: "POST",
                url: "/boardapp/payment_checkout/",
                async: false,
                data: formData,
                timeout: 15000,
            });
            request.done(function (data) {
                if (data.works) {
                    merchant_id = data.merchant_id;
                }
                console.log("Check out 성공");
            });
            request.fail(function (jqXHR, textStatus) {
                if (jqXHR.status == 404) {
                    alert("페이지가 존재하지 않습니다.1");
                } else if (jqXHR.status == 403) {
                    alert("로그인 해주세요.");
                } else {
                    alert("문제가 발생했습니다. 다시 시도해주세요.1");
                }
            });
            return merchant_id;
        }

 function ImpTransaction(e, merchant_id, imp_id, amount,status) {
            e.preventDefault();
            var formData = new FormData()
            formData.append('merchant_id', merchant_id);
            formData.append('imp_id', imp_id);
            formData.append('amount', amount);
            formData.append('status', status);

            var request = $.ajax({
                processData: false,
                contentType: false,
                type: "POST",
                url: "/boardapp/payment_res/",
                async: false,
                timeout: 15000,
                data: formData,
            });
            request.done(function (data) {
                if (data.works) {
                // 결제 완료시 할 동작 들
                console.log("payment_res 성공");
                }
            });
            request.fail(function (jqXHR, textStatus) {
                if (jqXHR.status == 404) {
                    alert("페이지가 존재하지 않습니다.2");
                } else if (jqXHR.status == 403) {
                    alert("로그인 해주세요.");
                } else {
                    console.log(merchant_id);
                    console.log(imp_id);
                    alert("문제가 발생했습니다. 다시 시도해주세요.2");
                }
            });
        }
 })
 function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});