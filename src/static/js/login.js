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

$(document).ready(function(){

	$('#signupform, #loginform').submit(function() {
    	var loginParams = JSON.stringify($(this).serializeObject());
    	$.ajax({
		    type: "POST",
		    url: $(this).attr('action'),
		    // The key needs to match your method's input parameter (case-sensitive).
		    data: loginParams,
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
		    success: function(data){
                console.log(data);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.responseText);
            },
		    failure: function(errMsg) {
                alert('hi');
		        console.log(errMsg);
		    }
		});
    	return false;
	});
});
