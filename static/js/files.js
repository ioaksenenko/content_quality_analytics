$(document).ready(function () {
    let files_names = [];
    let checked = $('[type="checkbox"][name="checked"]:checked');
    checked.each(function (i, e) {
        files_names.push($(e).val())
    });

    let text_input = $('#module-name');
    let module_name = text_input.val();

    if (files_names.length !== 0) {
        $('#join').prop('disabled', false);
        let csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        if (module_name !== '') {
            $.ajax({
                dataType: "json",
                method: "POST",
                url: "/del-last-module/",
                data: {
                    files_names: files_names,
                    module_name: module_name
                }
            }).done(function (response) {
                console.log(response);
            }).fail(function (response) {
                console.log(response);
            });
        } else {
            $.ajax({
                dataType: "json",
                method: "POST",
                url: "/return-deleted-files/",
                data: {
                    files_names: files_names
                }
            }).done(function (response) {
                console.log(response);
            }).fail(function (response) {
                console.log(response);
            });
        }
    }

    let analyze = $('#analyze');
    let check_all = $('#check-all');
    let checkboxes = $('input[type="checkbox"][name="checked"]');

    checkboxes.each(function (i, e) {
        if (!$(e).is(':checked')) {
            $(e).parent().parent().next().addClass('disabled');
        }
    });
    check_all.prop('indeterminate', checked.length !== checkboxes.length);

    checkboxes.change(disabled_submit);
    $('#module-type').change(disabled_submit);
    text_input.keyup(disabled_submit);
    disabled_submit();

    check_all.change(select);
});

function disabled_submit() {
    let submit = $('#join');
    let remove = $('#remove');
    let module_name = $('#module-name');
    let module_type = $('#module-type');
    let checked = $('[type="checkbox"][name="checked"]:checked');
    let check_all = $('#check-all');
    let checkboxes = $('input[type="checkbox"][name="checked"]');

    if ($(this).is(':checked')) {
        $(this).parent().parent().next().removeClass('disabled');
    } else {
        $(this).parent().parent().next().addClass('disabled');
    }

    if (checked.length !== 0) {
        check_all.prop('checked', true);
        check_all.prop('indeterminate', checked.length !== checkboxes.length);
        if (module_name.val() !== '' && module_type.val() !== 'unknown') {
            submit.prop('disabled', false);
        } else {
            submit.prop('disabled', true);
        }
        remove.prop('disabled', false);
    } else {
        check_all.prop('checked', false);
        check_all.prop('indeterminate', false);
        submit.prop('disabled', true);
        remove.prop('disabled', true);
    }
}


function select() {
    let checkboxes = $('input[type="checkbox"][name="checked"]');
    let checked = $('input[type="checkbox"][name="checked"]:checked');

    if (checked.length === 0) {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', true);
            $(this).parent().parent().next().removeClass('disabled');
            if ($('#module-name').val() !== '' && $('#module-type').val() !== 'unknown') {
                $('#join').prop('disabled', false);
            }
            $('#remove').prop('disabled', false);
        });
    } else {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', false);
            $(this).parent().parent().next().addClass('disabled');
            $('#join').prop('disabled', true);
            $('#remove').prop('disabled', true);
        });
    }
}


function remove_selected_files() {
    let files_names = [];
    let checked = $('[type="checkbox"][name="checked"]:checked');
    checked.each(function (i, e) {
        files_names.push($(e).val())
    });
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
            url: "/remove-selected-files/",
            data: {
                files_names: files_names
            }
        }).done(function (response) {
            console.log(response);
            console.log('before reloaded');
            location.reload();
            console.log('reloaded');
        }).fail(function (response) {
            console.log(response);
        });
}