function select() {
    var checkboxes = $('input[type="checkbox"][name="modules"]');
    var checked = $('input[type="checkbox"][name="modules"]:checked');
    if (checked.length !== checkboxes.length) {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', true);
            $('#analyze').prop('disabled', false);
        });
    } else {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', false);
            $('#analyze').prop('disabled', true);
        });
    }
}


$(document).ready(function () {
    $('#modules').submit(function () {
        $('#analyze').prop('disabled', true);
        var container = $('.container-fluid>.row:last>.col');
        console.log(container);
        container.append('<img src="http://denis-creative.com/wp-content/uploads/2017/10/loader.gif" class="mt-3" alt="loader"><p>Пожалуйста, подождите. Анализ может занять несколько минут... </p>');
    });

    if ($('input[type="checkbox"][name="modules"]:checked').length !== 0) {
        $('#analyze').prop('disabled', false);
    }

    $('input[type="checkbox"][name="modules"]').change(function () {
        if ($('input[type="checkbox"][name="modules"]:checked').length !== 0) {
            $('#analyze').prop('disabled', false);
        } else {
            $('#analyze').prop('disabled', true);
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