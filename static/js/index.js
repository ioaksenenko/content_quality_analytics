$(document).ready(function () {
    let files = $('#files');

    if (files.get(0).files.length !== 0) {
        $('#send').prop('disabled', false);
    } else {
        $('#send').prop('disabled', true);
    }

    files.on('change',function (e) {
        if (e.target.files.length !== 0) {
            $('#send').prop('disabled', false);
        } else {
            $('#send').prop('disabled', true);
        }
    });

    $(window).on('unload', function() {
        let csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $.ajax({
            dataType: "json",
            method: "POST",
            url: "/unload/",
            data: {}
        }).done(function (response) {
            console.log(response);
        }).fail(function (response) {
            console.log(response);
        });
    });
});

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}