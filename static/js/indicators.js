$(document).ready(function () {
    let next = $('#next');

    if ($('input[type="checkbox"][name="indicators"]:checked').length !== 0) {
        next.prop('disabled', false);
    }

    //let check_all = $('#check-all');
    let checkboxes = $('input[type="checkbox"][name="indicators"]');

    checkboxes.each(function (i, e) {
        if (!$(e).is(':checked')) {
            $(e).parent().parent().next().addClass('disabled');
            $(e).parent().parent().next().next().addClass('disabled');
        }
    });
    //check_all.prop('indeterminate', checked.length !== checkboxes.length);

    checkboxes.change(function () {
        if ($(this).is(':checked')) {
            $(this).parent().parent().next().removeClass('disabled');
            $(this).parent().parent().next().next().removeClass('disabled');
        } else {
            $(this).parent().parent().next().addClass('disabled');
            $(this).parent().parent().next().next().addClass('disabled');
        }
        //let check_all = $('#check-all');
        let checked = $('input[type="checkbox"][name="indicators"]:checked');
        let checkboxes = $('input[type="checkbox"][name="indicators"]');
        let next = $('#next');
        if (checked.length !== 0) {
            next.prop('disabled', false);
            //check_all.prop('checked', true);
            //check_all.prop('indeterminate', checked.length !== checkboxes.length);
        } else {
            next.prop('disabled', true);
            //check_all.prop('checked', false);
            //check_all.prop('indeterminate', false)
        }
    });

    //check_all.change(select);

    $('#indicators').submit(function () {
        let next = $('#next');
        let spinner = $('#spinner');

        next.prop('disabled', true);
        spinner.removeClass('d-none');

        /*next.empty();
        next.append(
            '<span class="spinner-grow spinner-grow-sm text-success mr-2" role="status" aria-hidden="true"></span>' +
            'Пожалуйста, подождите. Анализ может занять несколько минут...'
        );*/
    });
});


function select() {
    var checkboxes = $('input[type="checkbox"][name="indicators"]');
    var checked = $('input[type="checkbox"][name="indicators"]:checked');
    if (checked.length === 0) {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', true);
            $('#next').prop('disabled', false);
            $(this).parent().parent().next().removeClass('disabled');
            $(this).parent().parent().next().next().removeClass('disabled');
        });
    } else {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', false);
            $('#next').prop('disabled', true);
            $(this).parent().parent().next().addClass('disabled');
            $(this).parent().parent().next().next().addClass('disabled');
        });
    }
}