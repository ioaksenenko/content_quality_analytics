$(document).ready(function () {
    $('#indicator-name').keyup(check_indicator_name);
});

function check_indicator_name() {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let indicator_name = $('#indicator-name');
    let indicator_name_val = indicator_name.val();
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/check-indicator-name/",
        data: {
            'indicator-name': indicator_name_val
        }
    }).done(function (response) {
        if (!response['res']) {
            indicator_name.removeClass('is-invalid');
            if (indicator_name_val !== '') {
                indicator_name.addClass('is-valid');
            } else {
                indicator_name.removeClass('is-valid');
            }
        } else {
            indicator_name.removeClass('is-valid');
            if (indicator_name_val !== '') {
                indicator_name.addClass('is-invalid');
            } else {
                indicator_name.removeClass('is-invalid');
            }
        }
    }).fail(function (response) {
        console.log(response);
    });
}