 $(document).ready(function ($) {
    var uploadedFile = [];
     var UploadController = {
      classno: undefined,
      init: function () {
        this.bindEvent();
      },
    bindEvent: function () {


    $("#upload_button").on('click', function (ev) {
          $("#files").click();
        });

    $("#files").on('change', function (ev) {
        var target = document.getElementsByName('files[]');
        Array.prototype.push.apply(fileBuffer, target[0].files);
        $.each(target[0].files, function(index, file){
          if (!file.type.match('image.*')) {
            alert(file.name + '파일은 이미지가 아닙니다.');
          } else {
          console.log('success');
            var reader = new FileReader();
            reader.onload = function (e) {
              var html = '';
              html += '<div class="file">';
              html += '<span><img src="' + e.target.result + '"></span>';
              html += '<a href="#" id="removeImg" class="removeBtn">╳</a>';
              html += '</div>';
              $('.fileList').append(html);

              if ($('.fileList').find('div.file').length > 0) {
                  $('#finish_button').show();
                } else {
                  $('#finish_button').hide();
                }
            }
            reader.readAsDataURL(file);
          }
        });

        $("#files").replaceWith( $("#files").clone(true));
        $("#files").val('');
      });
    $(document).on('click', '#removeImg', function(){
            var fileIndex = $(this).parent().index();
            fileBuffer.splice(fileIndex,1);
            $('.fileList>div:eq('+fileIndex+')').remove();
          });
     }
    }
    $('#finish_button').on('click', function (ev) {
          var files = [];
           var form = $('#fileUploadForm')[0];
            var formData = new FormData(form);
          $.each(fileBuffer, function(index, file) {
            var fileName = file.name;
            var fileEx = fileName.slice(fileName.indexOf(".") + 1).toLowerCase();


            formData.append('img_file', file);
            formData.append('fd_name2', $('#fd_name2').val());
            formData.append('unit', $('#unit').val());
            formData.append('bookname', $('#bookname').val());
            formData.append('category_id', $('#category_id').val());

            });
            $.ajax({
              url: "/boardapp/upload_res/",
              processData: false,
              contentType: false,
              data: formData,
              type: 'POST',
              async: false,
              success: function (response) {
                console.log('success transfer');
              },
              error:  function (error) {
                console.log('error occured');
                alert('파일 업데이트에 실패하였습니다. 관리자에게 문의하여 주세요');
              },
              complete: function () {
                alert('수업자료가 등록되었습니다. 관리자의 승인 후 페이지에 표기됩니다.');
                window.location.href = "/boardapp/";
              }
            });

        });
    var fileBuffer = [];
    UploadController.init();
   });
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