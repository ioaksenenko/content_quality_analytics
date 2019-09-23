$(document).ready(function () {
    let files_names = [];
    let checked = $('[type="checkbox"][name="checked"]:checked');
    checked.each(function (i, e) {
        files_names.push($(e).val())
    });

    let text_input = $('#module-name');
    let module_name = text_input.val();

    if (files_names.length !== 0 && module_name !== '') {
        $('#join').prop('disabled', false);
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
            url: "/del_last_module/",
            data: {
                files_names: files_names,
                module_name: module_name
            }
        }).done(function (response) {
            console.log(response);
        }).fail(function (response) {
            console.log(response);
        });
    }

     $('[type="checkbox"][name="checked"]').change(disabled_submit);
    text_input.keyup(disabled_submit);

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

function disabled_submit() {
    let submit = $('#join');
    let module_name = $('#module-name');
    let checked = $('[type="checkbox"][name="checked"]:checked');
    if (module_name.val() !== '' && checked.length !== 0) {
        submit.prop('disabled', false);
    } else {
        submit.prop('disabled', true);
    }
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function select() {
    var checkboxes = $('input[type="checkbox"][name="checked"]');
    var checked = $('input[type="checkbox"][name="checked"]:checked');
    if (checked.length !== checkboxes.length) {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', true);
            if ($('#module-name').val() !== '') {
                $('#join').prop('disabled', false);
            }
        });
    } else {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', false);
            $('#join').prop('disabled', true);
        });
    }
}