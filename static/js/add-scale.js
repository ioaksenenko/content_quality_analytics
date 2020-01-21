$(document).ready(function () {
    $('[type="radio"][name="scale-type"]').change(function () {
        let ordinal_scale_fields = $('#ordinal-scale-fields');
        let interval_scale_fields = $('#interval-scale-fields');
        let min_val = $('#min-val');
        let max_val = $('#max-val');
        let step = $('#step');
        let values = $('[name="values"]');
        if (this.value === 'ordinal-scale') {
            ordinal_scale_fields.removeClass('d-none');
            if (!interval_scale_fields.hasClass('d-none')) {
                interval_scale_fields.addClass('d-none');
            }
            min_val.attr('required', true);
            max_val.attr('required', true);
            step.attr('required', true);
            values.each(function (i, e) {
               $(e).attr('required', false);
            });
        } else if (this.value === 'interval-scale') {
            interval_scale_fields.removeClass('d-none');
            if (!ordinal_scale_fields.hasClass('d-none')) {
                ordinal_scale_fields.addClass('d-none');
            }
            min_val.attr('required', false);
            max_val.attr('required', false);
            step.attr('required', false);
            values.each(function (i, e) {
               $(e).attr('required', true);
            });
        }
    });
    $('#scale-id').keyup(check_scale_id);
});

function add_field() {
    let input = $('#interval-scale-fields>.col>.row:last input');
    let id = input.attr('id');
    let fragments = id.split('-');
    let n = parseInt(fragments[fragments.length - 1]) + 1;

    $('#interval-scale-fields>.col').append(
        '<div class="row align-items-center mt-3">' +
        '    <div class="col-2 h-100">' +
        '        <div class="form-group h-100 w-100 p-0 m-0">' +
        '            <label for="value-' + n + '" class="d-none"></label>' +
        '            <input type="text" class="form-control mt-auto mb-0" id="value-' + n + '" name="values" placeholder="' + n + '">' +
        '        </div>' +
        '    </div>' +
        '    <div class="col-auto p-0 m-0 h-100">' +
        '        <a href="#" class="w-100 h-100 m-0 p-0" onclick="remove_field(\'value-' + n + '\')"><i class="fas fa-minus-circle m-0 p-0 h-100" style="font-size: 2rem; cursor: pointer"></i></a>' +
        '    </div>' +
        '</div>'
    );

    $('#value-' + n).attr('required', true);
}

function remove_field(id) {
    $('#' + id).parent().parent().parent().remove();
}

function check_scale_id() {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let scale_id = $('#scale-id');
    let scale_id_val = scale_id.val();
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/check-scale-id/",
        data: {
            'scale-id': scale_id_val
        }
    }).done(function (response) {
        if (!response['res']) {
            scale_id.removeClass('is-invalid');
            if (scale_id_val !== '') {
                scale_id.addClass('is-valid');
            } else {
                scale_id.removeClass('is-valid');
            }
        } else {
            scale_id.removeClass('is-valid');
            if (scale_id_val !== '') {
                scale_id.addClass('is-invalid');
            } else {
                scale_id.removeClass('is-invalid');
            }
        }
    }).fail(function (response) {
        console.log(response);
    });
}