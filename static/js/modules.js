$(document).ready(function () {
    /*$('#modules').submit(function () {
        $('#next').prop('disabled', true);
        var container = $('.container-fluid>.row:last>.col');
        console.log(container);
        container.append('<img src="http://denis-creative.com/wp-content/uploads/2017/10/loader.gif" class="mt-3" alt="loader"><p>Пожалуйста, подождите. Анализ может занять несколько минут... </p>');
    });*/

    //let msg_src = $('#msg-src');
    let msg = $('#msg');
    let next = $('#next');
    let checkboxes = $('input[type="checkbox"][name="modules"]');
    let enabled = $('input[type="checkbox"][name="modules"]:enabled');
    let checked = $('input[type="checkbox"][name="modules"]:checked');
    let check_all = $('#check-all');

    //let join = $('#join');
    //let checkboxes_for_join = $('input[type="checkbox"][name="modules-for-join"]');
    //let checked_for_join = $('input[type="checkbox"][name="modules-for-join"]:checked');
    //let check_all_for_join = $('#check-all-for-join');


    checked.each(function (i, e) {
        if ($(e).parent().parent().next().next().find('select').val() === 'unknown') {
            msg.removeClass('d-none');
            next.prop('disabled', true);
        }
        //if ($(e).parent().parent().next().next().next().find('span').text() === 'Не определён') {
            //msg_src.removeClass('d-none');
            //next.prop('disabled', true);
        //}
    });
    enabled.each(function (i, e) {
        if (!$(e).is(':checked')) {
            $(e).parent().parent().next().addClass('disabled');
            $(e).parent().parent().next().next().find('select').prop('disabled', true);
            $(e).parent().parent().next().next().next().find('span').addClass('disabled');
        }
    });
    check_all.prop('indeterminate', checked.length !== checkboxes.length);

    //check_all_for_join.prop('indeterminate', checked.length !== checkboxes.length);

    enabled.change(function () {
        let msg = $('#msg');
        let check_all = $('#check-all');
        let checked = $('input[type="checkbox"][name="modules"]:checked');
        let enabled = $('input[type="checkbox"][name="modules"]:enabled');
        let checkboxes = $('input[type="checkbox"][name="modules"]');
        let next = $('#next');

        if ($(this).is(':checked')) {
            $(this).parent().parent().next().removeClass('disabled');
            let select = $(this).parent().parent().next().next().find('select');
            $(this).parent().parent().next().next().next().find('span').removeClass('disabled');
            //$(this).parent().parent().next().next().next().find('span').addClass('red');
            select.prop('disabled', false);
            next.prop('disabled', false);
            if (select.val() === 'unknown') {
                msg.removeClass('d-none');
                next.prop('disabled', true);
            }
            //if ($(this).parent().parent().next().next().next().find('span').text() === 'Не определён') {
                //msg_src.removeClass('d-none');
                //next.prop('disabled', true);
            //}
        } else {
            $(this).parent().parent().next().addClass('disabled');
            $(this).parent().parent().next().next().find('select').prop('disabled', true);
            $(this).parent().parent().next().next().next().find('span').addClass('disabled');
            //$(this).parent().parent().next().next().next().find('span').removeClass('red');
            msg.addClass('d-none');
            //msg_src.addClass('d-none');
            next.prop('disabled', false);
            checked.each(function (i, e) {
                if ($(e).parent().parent().next().next().find('select').val() === 'unknown') {
                    msg.removeClass('d-none');
                    next.prop('disabled', true);
                }
                //if ($(e).parent().parent().next().next().next().find('span').text() === 'Не определён') {
                    //msg_src.removeClass('d-none');
                    //next.prop('disabled', true);
                //}
            });
        }
        if (checked.length !== 0) {
            check_all.prop('checked', true);
            check_all.prop('indeterminate', checked.length !== checkboxes.length);
        } else {
            next.prop('disabled', true);
            check_all.prop('checked', false);
            check_all.prop('indeterminate', false);
        }
    });

    /*checkboxes_for_join.change(function () {
        let check_all_for_join = $('#check-all-for-join');
        let checked_for_join = $('input[type="checkbox"][name="modules-for-join"]:checked');
        let checkboxes_for_join = $('input[type="checkbox"][name="modules-for-join"]');
        let join = $('#join');
        let split = $('#split');

        if (checked_for_join.length !== 0) {
            check_all_for_join.prop('checked', true);
            check_all_for_join.prop('indeterminate', checked_for_join.length !== checkboxes_for_join.length);
            split.removeClass('d-none');
        } else {
            check_all_for_join.prop('checked', false);
            check_all_for_join.prop('indeterminate', false);
            if (!split.hasClass('d-none')) {
                split.addClass('d-none');
            }
        }

        if (checked_for_join.length > 1) {
            join.removeClass('d-none');
        } else if (!join.hasClass('d-none')) {
            join.addClass('d-none');
        }
    });*/

    check_all.change(select);
    //check_all_for_join.change(select_for_join);

    $('select').change(function () {
        let msg = $('#msg');
        let next = $('#next');
        let checked = $('input[type="checkbox"][name="modules"]:checked');

        if ($(this).val() === 'unknown') {
            msg.removeClass('d-none');
            next.prop('disabled', true);
        } else {
            msg.addClass('d-none');
            next.prop('disabled', false);
            checked.each(function (i, e) {
                if ($(e).parent().parent().next().next().find('select').val() === 'unknown') {
                    msg.removeClass('d-none');
                    next.prop('disabled', true);
                }
            });
        }
    });

    move_files_to_tmp();

    $('#element-name').keyup(function () {
        $(this).removeClass('is-invalid');
    });

    $('#modules').submit(function () {
        let next = $('#next');
        let spinner = $('#spinner');

        next.prop('disabled', true);
        spinner.removeClass('d-none');
    });
});


function select() {
    let msg = $('#msg');
    //let msg_src = $('#msg-src');
    let checkboxes = $('input[type="checkbox"][name="modules"]');
    let enabled = $('input[type="checkbox"][name="modules"]:enabled');
    let checked = $('input[type="checkbox"][name="modules"]:checked');
    let next = $('#next');
    let check_all = $('#check-all');
    msg.addClass('d-none');
    //msg_src.addClass('d-none');
    if (checked.length === 0) {
        next.prop('disabled', false);
        enabled.each(function (i, e) {
            $(e).prop('checked', true);
            $(this).parent().parent().next().removeClass('disabled');
            $(this).parent().parent().next().next().find('select').prop('disabled', false);
            $(this).parent().parent().next().next().next().find('span').removeClass('disabled');
            //$(this).parent().parent().next().next().next().find('span').addClass('red');
            if ($(e).parent().parent().next().next().find('select').val() === 'unknown') {
                msg.removeClass('d-none');
                next.prop('disabled', true);
            }
            //if ($(e).parent().parent().next().next().next().find('span').text() === 'Не определён') {
                //msg_src.removeClass('d-none');
                //next.prop('disabled', true);
            //}
        });
        check_all.prop('checked', true);
        check_all.prop('indeterminate', checked.length !== checkboxes.length);
    } else {
        enabled.each(function (i, e) {
            $(e).prop('checked', false);
            next.prop('disabled', true);
            $(this).parent().parent().next().addClass('disabled');
            $(this).parent().parent().next().next().find('select').prop('disabled', true);
            $(this).parent().parent().next().next().next().find('span').addClass('disabled');
            //$(this).parent().parent().next().next().next().find('span').removeClass('red');
        });
        check_all.prop('checked', false);
    }
}


function select_for_join() {
    let checked_for_join = $('input[type="checkbox"][name="modules-for-join"]:checked');
    let checkboxes_for_join = $('input[type="checkbox"][name="modules-for-join"]');
    let join = $('#join');
    let split = $('#split');

    if (checked_for_join.length === 0) {
        join.removeClass('d-none');
        checkboxes_for_join.each(function (i, e) {
            $(e).prop('checked', true);
        });
        split.removeClass('d-none');
    } else {
        if (!join.hasClass('d-none')) {
            join.addClass('d-none');
        }
        checkboxes_for_join.each(function (i, e) {
            $(e).prop('checked', false);
        });
        if (!split.hasClass('d-none')) {
            split.addClass('d-none');
        }
    }
}


function move_files_to_tmp() {
    let csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let checked = [];
    $('input[type="checkbox"][name="modules"]:checked').each(function (i, e) {
        checked.push($(e).val())
    });
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/move-files-to-tmp/",
        data: {
            'checked': checked
        }
    }).done(function (response) {
        console.log(response);
    }).fail(function (response) {
        console.log(response);
    });
}


function join_elements() {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let checked = [];
    $('input[type="checkbox"][name="modules-for-join"]:checked').each(function (i, e) {
        checked.push($(e).val())
    });
    let element_name = $('#element-name');
    let element_name_val = element_name.val();
    if (element_name_val !== '') {
        $.ajax({
            dataType: "html",
            method: "POST",
            url: "/join-elements/",
            data: {
                'checked': checked,
                'element-name': element_name_val
            }
        }).done(function (response) {
            location.reload();
        }).fail(function (response) {
            console.log(response);
        });
    } else {
        element_name.addClass('is-invalid');
    }
}


function split_elements() {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let checked = [];
    $('input[type="checkbox"][name="modules-for-join"]:checked').each(function (i, e) {
        checked.push($(e).val())
    });
    $.ajax({
        dataType: "html",
        method: "POST",
        url: "/split-elements/",
        data: {
            'checked': checked
        }
    }).done(function (response) {
        location.reload();
    }).fail(function (response) {
        console.log(response);
    });
}