$(document).ready(function () {
    $(window).on('beforeunload', function() {
        let csrftoken = Cookies.get('csrftoken');
        console.log(csrftoken);
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
        let csrftoken = Cookies.get('csrftoken');
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
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}