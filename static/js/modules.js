function select() {
    var checkboxes = $('input[type="checkbox"][name="modules"]');
    var checked = $('input[type="checkbox"][name="modules"]:checked');
    if (checked.length !== checkboxes.length) {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', true);
        });
    } else {
        checkboxes.each(function (i, e) {
            $(e).prop('checked', false);
        });
    }
}


$(document).ready(function () {
    $('#modules').submit(function () {
        $('#analyze').prop('disabled', true);
        var container = $('.container-fluid>.row>.col');
        container.append('<img src="http://denis-creative.com/wp-content/uploads/2017/10/loader.gif" class="mt-3" alt="loader"><p>Пожалуйста, подождите. Анализ может занять несколько минут... </p>');
    });
});