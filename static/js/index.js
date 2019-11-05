$(document).ready(function () {
    let files = $('#files');

    if (files.get(0).files.length !== 0) {
        $('#send').prop('disabled', false);
    } else {
        $('#send').prop('disabled', true);
    }

    files.on('change',function (e) {
        if (e.target.files.length !== 0) {
            $('#send').prop('disabled', false);
        } else {
            $('#send').prop('disabled', true);
        }
    });
});