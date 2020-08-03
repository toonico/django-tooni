function idCheck() {
	if (!$('#username').val())
	{
		alert("ID를 입력해 주시기 바랍니다.");
		return;
	}

	$.ajax({
		type: "POST",
		url: "/boardapp/user_register_idcheck/",
		data: {
			'username': $('#username').val(),
			'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
		},
		success: function(response) {
			$('#idcheck-result').html(response);
		},
	});	
}

function changeEmailDomain() {
	$('#email_domain').val($('#email_selection').val());	
}

function cancelUserRegister() {
	var result = confirm("회원가입을 취소하시겠습니까?");	

	if (result)
	{
		$(location).attr('href', '/boardapp/login');
	}
}

function userRegister() {
	if (!$('#username').val())
	{
		alert("아이디를 입력해 주시기 바랍니다.");
		return;
	}
	if (!$('#IDCheckResult').val()) {
		alert("ID 중복체크를 먼저 진행해 주시기 바랍니다.");
		return;
	}
	if (!$('#password').val()) {
		alert("비밀번호를 입력해 주시기 바랍니다.");
		return;
	}
	if($('#password').val().length < 8) {
		alert('비밀번호는 최소 8자 이상이여야 합니다.');
		alert($('#password').val().length );
		return;
	}
	if ($('#password').val() != $('#password_check').val()) {
		alert("비밀번호가 일치하지 않습니다.");
		return;
	}
	if (!$('#last_name').val())
	{
		alert("이름을 입력해 주시기 바랍니다.");
		return;
	}
	if (!$('#phone1').val() || !$('#phone2').val() || !$('#phone3').val())
	{
		alert("전화번호를 올바르게 입력해 주시기 바랍니다.");
		return;
	}
	if (!$('#email_id').val() || !$('#email_domain').val())
	{
		alert("E-mail 주소를 올바르게 입력해 주시기 바랍니다.");
		return;
	}
	if (!$('#birth_year').val() || !$('#birth_month').val() || !$('#birth_day').val())
	{
		alert("생년월일을 올바르게 입력해 주시기 바랍니다.");
		return;
	}

	$('#phone').val($('#phone1').val() + "-" + $('#phone2').val() + "-" + $('#phone3').val());
	$('#email').val($('#email_id').val() + "@" + $('#email_domain').val());

	$('#register_form').submit();
}

function changePassword() {
	if (!$('#id_old_password').val()) {
		alert("비밀번호를 입력해 주시기 바랍니다.");
		return;
	}
	if ($('#id_new_password1').val() != $('#id_new_password2').val()) {
		alert("비밀번호가 일치하지 않습니다.");
		return;
	}

	$('#password_change_form').submit();
}
///////////

$(function () {
            var IMP = window.IMP;
            // 가맹점 코드
            IMP.init('imp68762150');

            $('.charge-button').on('click', function (e) {
                var amount = parseInt($('.charge-total #total').text().replace(',', '').slice(0, -1));
                var type = $('.charge-type input:checked').val();
                var merchant_id = AjaxStoreTransaction(e, amount, type);

                if (merchant_id !== '') {
                    IMP.request_pay({
                        pg: 'html5_inicis',
                        escrow: false,
                        digital: true,
                        pay_method: type,
                        merchant_uid: merchant_id,
                        name: '포인트' + amount + '원 충전',
                        amount: amount
                    }, function (rsp) {
                        if (rsp.success) {
                            var msg = '결제가 완료되었습니다.';
                            msg += '고유ID : ' + rsp.imp_uid;
                            msg += '상점 거래ID : ' + rsp.merchant_uid;
                            msg += '결제 금액 : ' + rsp.paid_amount;
                            msg += '카드 승인번호 : ' + rsp.apply_num;
                            ImpTransaction(e, rsp.merchant_uid, rsp.imp_uid, rsp.paid_amount);
                        } else {
                            var msg = '결제에 실패하였습니다.';
                            msg += '에러내용 : ' + rsp.error_msg;
                            console.log(msg);
                        }
                    });
                }
            });
        });

        function AjaxStoreTransaction(e, amount, type) {
            e.preventDefault();
            var merchant_id = '';
            var request = $.ajax({
                method: "POST",
                url: '{% url "point_checkout" %}',
                async: false,
                data: {
                    amount: amount,
                    type: type,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                }
            });
            request.done(function (data) {
                if (data.works) {
                    merchant_id = data.merchant_id;
                }
            });
            request.fail(function (jqXHR, textStatus) {
                if (jqXHR.status == 404) {
                    alert("페이지가 존재하지 않습니다.");
                } else if (jqXHR.status == 403) {
                    alert("로그인 해주세요.");
                } else {
                    alert("문제가 발생했습니다. 다시 시도해주세요.");
                }
            });
            return merchant_id;
        }

        function ImpTransaction(e, merchant_id, imp_id, amount) {
            e.preventDefault();
            var request = $.ajax({
                method: "POST",
                url: '{% url "point_validation" %}',
                async: false,
                data: {
                    merchant_id: merchant_id,
                    imp_id: imp_id,
                    amount: amount,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                }
            });
            request.done(function (data) {
                if (data.works) {
                }
            });
            request.fail(function (jqXHR, textStatus) {
                if (jqXHR.status == 404) {
                    alert("페이지가 존재하지 않습니다.");
                } else if (jqXHR.status == 403) {
                    alert("로그인 해주세요.");
                } else {
                    alert("문제가 발생했습니다. 다시 시도해주세요.");
                }
            });
        }