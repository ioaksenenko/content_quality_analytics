$(document).ready(function () {
    let files = $('#files');
    let moodle_send = $('#moodle-send');
    let course_id = $('#course-id');
    let spinner = $('#spinner');

    /*if (files.get(0).files.length !== 0) {
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
    });*/

    course_id.keyup(function () {
        let moodle_send = $('#moodle-send');
        let value = $(this).val();
        if (value !== '' && /^[1-9]+\d*$/.test(value)) {
            moodle_send.prop('disabled', false);
        } else {
            moodle_send.prop('disabled', true);
        }
    });

    moodle_send.click(function () {
        let spinner = $('#spinner');
        let moodle_form = $('#moodle-form');

        $(this).prop('disabled', true);
        spinner.removeClass('d-none');
        moodle_form.submit();
    });

    let value = course_id.val();
    if (value !== '' && /^[1-9]+\d*$/.test(value)) {
        moodle_send.prop('disabled', false);
    } else {
        moodle_send.prop('disabled', true);
    }
});