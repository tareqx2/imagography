$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function clearPopup() {
    $('.popup.visible').addClass('transitioning').removeClass('visible');
    $('html').removeClass('overlay');

    setTimeout(function () {
        $('.popup').removeClass('transitioning');
    }, 200);
}


$(document).ready(function(){
    var resetPasswordModal = $('#password_modal');
    if(resetPasswordModal.length !=0){
        resetPasswordModal.modal({
          backdrop: 'static',
          keyboard: false
        });
    }

	$('form').submit(function() {
    	var params = JSON.stringify($(this).serializeObject());
        var parentPanel = $(this).closest('.panel.panel-info,.modal');
        if(parentPanel.length!=0){
            var rect = {
                height: parentPanel.outerHeight(),
                width: parentPanel.outerWidth(),
                top: parentPanel.offset().top,
                left: parentPanel.offset().left
            };

            var overlay = $('.form-overlay');
            
            overlay.className = 'form-overlay';
            $(overlay).css('display','block');
            $(overlay).css('top',rect.top);
            $(overlay).css('left',rect.left);
            $(overlay).css('height',rect.height);
            $(overlay).css('width',rect.width);
        }
    	$.ajax({
		    type: "POST",
		    url: $(this).attr('action'),
		    // The key needs to match your method's input parameter (case-sensitive).
		    data: params,
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
		    success: function(data){
                var overlay = $('.form-overlay');
                if(overlay.length!=0)
                    overlay.css('display','none');
                if(data.params){
                    window.location.replace(data.redirectUrl+"?"+data.params);
                }
                else{
                    window.location.replace(data.redirectUrl);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                $('.form-overlay').css('display','none');
                $('html').addClass('overlay');
                $('.popup-overlay').css('display','block');
                var errorObj = jQuery.parseJSON(jqXHR.responseText);
                var activePopup = $('#error-popup');
                $(activePopup).addClass('visible');
                $('.popup-title.error',activePopup).text(errorObj.message);
            },
		    failure: function(errMsg) {
                $('.form-overlay').css('display','none');
		        console.log(errMsg);
		    }
		});
    	return false;
	});

    $('[data-popup-target]').click(function () {
        $('html').addClass('overlay');
        $('.popup-overlay').css('display','block');

        var activePopup = $(this).attr('data-popup-target');
        $(activePopup).addClass('visible');
        return false;
    });

    $(document).keyup(function (e) {
        if (e.keyCode == 27 && $('html').hasClass('overlay')) {
            clearPopup();
        }
    });

    $('.popup-exit').click(function () {
        clearPopup();

    });

    $('.popup-overlay').click(function () {
        clearPopup();
    });
});
