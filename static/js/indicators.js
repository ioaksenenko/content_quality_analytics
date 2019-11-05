$(document).ready(function () {
    if ($('input[type="checkbox"][name="indicators"]:checked').length !== 0) {
        $('#next').prop('disabled', false);
    }

    $('input[type="checkbox"][name="indicators"]').change(function () {
        if ($('input[type="checkbox"][name="indicators"]:checked').length !== 0) {
            $('#next').prop('disabled', false);
        } else {
            $('#next').prop('disabled', true);
        }
    });

    $('#indicators').submit(function () {
        let next = $('#next');
        next.prop('disabled', true);
        next.empty();
        next.append(
            '<span class="spinner-grow spinner-grow-sm text-success mr-2" role="status" aria-hidden="true"></span>' +
            'Пожалуйста, подождите. Анализ может занять несколько минут...'
        );
    });
});


function select() {
    var checkboxes = $('input[type="checkbox"][name="indicators"]');
    var checked = $('input[type="checkbox"][name="indicators"]:checked');
    if (checked.length !== checkboxes.length) {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', true);
            $('#next').prop('disabled', false);
        });
    } else {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', false);
            $('#next').prop('disabled', true);
        });
    }
}