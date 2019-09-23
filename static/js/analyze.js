$(document).ready(function () {
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

    $(window).on('load', function() {
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
            url: "/load/",
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