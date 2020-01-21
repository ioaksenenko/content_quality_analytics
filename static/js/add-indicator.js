$(document).ready(function () {
    $('#indicator-id').keyup(check_indicator_id);
});

function check_indicator_id() {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let indicator_id = $('#indicator-id');
    let indicator_id_val = indicator_id.val();
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/check-indicator-id/",
        data: {
            'indicator-id': indicator_id_val
        }
    }).done(function (response) {
        if (!response['res']) {
            indicator_id.removeClass('is-invalid');
            if (indicator_id_val !== '') {
                indicator_id.addClass('is-valid');
            } else {
                indicator_id.removeClass('is-valid');
            }
        } else {
            indicator_id.removeClass('is-valid');
            if (indicator_id_val !== '') {
                indicator_id.addClass('is-invalid');
            } else {
                indicator_id.removeClass('is-invalid');
            }
        }
    }).fail(function (response) {
        console.log(response);
    });
}