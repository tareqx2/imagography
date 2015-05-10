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

	$('form').submit(function() {
    	var params = JSON.stringify($(this).serializeObject());
    	$.ajax({
		    type: "POST",
		    url: $(this).attr('action'),
		    // The key needs to match your method's input parameter (case-sensitive).
		    data: params,
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
		    success: function(data){
                if(data.params){
                    window.location.replace(data.redirectUrl+"?"+data.params);
                }
                else{
                    window.location.replace(data.redirectUrl);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.responseText);
            },
		    failure: function(errMsg) {
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
