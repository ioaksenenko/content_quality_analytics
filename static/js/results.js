$(document).ready(function () {
    $('#results').submit(function () {
        let next = $('#next');
        let spinner = $('#spinner');

        next.prop('disabled', true);
        spinner.removeClass('d-none');
    });
});