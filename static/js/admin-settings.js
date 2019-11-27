$(document).ready(function () {
    $('[id^="scale-name-"]').each(function (i, e) {
        let scale_name = $(e).val();
        $('[type="radio"][name="scale-type-' + scale_name + '"]').change(function () {
            let ordinal_scale_fields = $('#ordinal-scale-fields-' + scale_name);
            let interval_scale_fields = $('#interval-scale-fields-' + scale_name);
            let min_val = $('#min-val-' + scale_name);
            let max_val = $('#max-val-' + scale_name);
            let step = $('#step-' + scale_name);
            let values = $('[name="values-' + scale_name + '"]');
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
        $('#scale-name-' + scale_name).keyup({scale_name: scale_name}, check_scale_name);
    });
    $('[id^="indicator-name-"]').each(function (i, e) {
        let indicator_name = $(e).val();
        $('#indicator-name-' + indicator_name).keyup({indicator_name: indicator_name}, check_indicator_name);
    });
    $('[id^="indicator-show-"]').each(function (i, e) {
        $(e).click(function (e) {
            $(e.target).attr('checked', !$(e.target).attr('checked'));
            $(e.target).val($(e.target).attr('checked') === 'checked' ? 'on'  : 'off');
        });
    });
});

function add_field(scale_name) {
    let input = $('#interval-scale-fields-' + scale_name + '>.col>.row:last input');
    let id = input.attr('id');
    let fragments = id.split('-');
    let n = parseInt(fragments[fragments.length - 1]) + 1;

    $('#interval-scale-fields-' + scale_name + '>.col').append(
        '<div class="row mt-3">' +
        '    <div class="col h-100">' +
        '        <div class="form-group h-100 w-100 p-0 m-0">' +
        '            <label for="value-' + scale_name + '-' + n + '" class="d-none"></label>' +
        '            <input type="text" class="form-control mt-auto mb-0" id="value-' + scale_name + '-' + n + '" name="values-' + scale_name + '" placeholder="' + n + '">' +
        '            <div class="invalid-feedback" id="invalid-feedback-' + scale_name + '-' + n + '"></div>' +
        '        </div>' +
        '    </div>' +
        '    <div class="col-auto p-0 m-0 h-100 mr-3 mt-1">' +
        '        <a href="#" class="w-100 h-100 m-0 p-0" onclick="remove_field(\'value-' + scale_name + '-' + n + '\')"><i class="fas fa-minus-circle m-0 p-0 h-100" style="font-size: 2rem; cursor: pointer"></i></a>' +
        '    </div>' +
        '</div>'
    );

    $('#value-' + scale_name + '-' + n).attr('required', true);
}

function remove_field(id) {
    $('#' + id).parent().parent().parent().remove();
}

function check_scale_name(e) {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let scale_name = $('#scale-name-' + e.data.scale_name);
    let scale_name_val = scale_name.val();
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/check-scale-name/",
        data: {
            'scale-name': scale_name_val
        }
    }).done(function (response) {
        if (!response['res'] || e.data.scale_name === scale_name_val) {
            scale_name.removeClass('is-invalid');
            if (scale_name_val !== '') {
                scale_name.addClass('is-valid');
            } else {
                scale_name.removeClass('is-valid');
            }
        } else {
            scale_name.removeClass('is-valid');
            if (scale_name_val !== '') {
                scale_name.addClass('is-invalid');
            } else {
                scale_name.removeClass('is-invalid');
            }
        }
    }).fail(function (response) {
        console.log(response);
    });
}

function change_scale(scale_name) {
    $('#modal-' + scale_name).modal('show');
}

function save_scale(old_scale_name) {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    let scale_name_field = $('#scale-name-' + old_scale_name);
    let scale_type_field = $('[name="scale-type-' + old_scale_name + '"]:checked');
    let min_val_field = $('#min-val-' + old_scale_name);
    let max_val_field = $('#max-val-' + old_scale_name);
    let step_field = $('#step-' + old_scale_name);
    let values_fields = $('[name="values-' + old_scale_name + '"]');

    let invalid_feedback_name = $('#invalid-feedback-' + old_scale_name + '-name');
    let invalid_feedback_min = $('#invalid-feedback-' + old_scale_name + '-min');
    let invalid_feedback_max = $('#invalid-feedback-' + old_scale_name + '-max');
    let invalid_feedback_step = $('#invalid-feedback-' + old_scale_name + '-step');

    invalid_feedback_name.empty();
    invalid_feedback_min.empty();
    invalid_feedback_max.empty();
    invalid_feedback_step.empty();

    min_val_field.removeClass('is-valid');
    min_val_field.removeClass('is-invalid');
    max_val_field.removeClass('is-valid');
    max_val_field.removeClass('is-invalid');
    step_field.removeClass('is-valid');
    step_field.removeClass('is-invalid');

    let scale_name =  scale_name_field.val();
    let scale_type =  scale_type_field.val();
    let min_val =  min_val_field.val();
    let max_val =  max_val_field.val();
    let step =  step_field.val();
    let values = [];
    values_fields.each(function (i, e) {
        values.push($(e).val());
        $(e).removeClass('is-valid');
        $(e).removeClass('is-invalid');
    });

    let modal_body = $('#modal-' + old_scale_name + ' .modal-body');
    let msg = $('[id^="msg-' + old_scale_name + '-"]');
    msg.each(function (i, e) {
        $(e).delete();
    });
    let feedback = $('[id^="invalid-feedback-' + old_scale_name + '-"]');
    feedback.each(function (i, e) {
        $(e).empty();
    });

    if (scale_name !== '' && !scale_name_field.hasClass('is-invalid')) {
        if (scale_type === 'ordinal-scale') {
            if (min_val !== '' && max_val !== '' && step !== '') {
                if (/^-?\d+([.,]\d+)?([eE][+-]\d+)?$/.test(min_val) && /^-?\d+([.,]\d+)?([eE][+-]\d+)?$/.test(max_val) && /^\d+([.,]\d+)?([eE][+-]\d+)?$/.test(step)) {
                    let min = parseFloat(min_val);
                    let max = parseFloat(max_val);
                    let step_val = parseFloat(step);
                    if (max <= min) {
                        if (!min_val_field.hasClass('is-invalid')) {
                            min_val_field.addClass('is-invalid');
                        }
                        if (!max_val_field.hasClass('is-invalid')) {
                            max_val_field.addClass('is-invalid');
                        }
                        invalid_feedback_min.append('<p>Максимальное значение шкалы должно быть больше минимального.</p>');
                        invalid_feedback_max.append('<p>Максимальное значение шкалы должно быть больше минимального.</p>');
                    } else if ((max - min) < step_val) {
                        if (!step_field.hasClass('is-invalid')) {
                            step_field.addClass('is-invalid');
                        }
                        invalid_feedback_step.append('<p>Значение шага должно быть меньше разности максимального и минимально значения.</p>');
                    }
                } else {
                    if (!/^-?\d+([.,]\d+)?([eE][+-]\d+)?$/.test(min_val)) {
                        if (!min_val_field.hasClass('is-invalid')) {
                            min_val_field.addClass('is-invalid');
                        }
                        invalid_feedback_min.append('<p>Неверный формат минимального значения шкалы.</p>');
                    }
                    if (!/^-?\d+([.,]\d+)?([eE][+-]\d+)?$/.test(max_val)) {
                        if (!max_val_field.hasClass('is-invalid')) {
                            max_val_field.addClass('is-invalid');
                        }
                        invalid_feedback_max.append('<p>Неверный формат максимального значения шкалы.</p>');
                    }
                    if (!/^\d+([.,]\d+)?([eE][+-]\d+)?$/.test(step)) {
                        if (!step_field.hasClass('is-invalid')) {
                            step_field.addClass('is-invalid');
                        }
                        invalid_feedback_step.append('<p>Неверный формат шага шкалы.</p>');
                    }
                }
            } else {
                if (min_val === '') {
                    if (!min_val_field.hasClass('is-invalid')) {
                        min_val_field.addClass('is-invalid');
                    }
                    invalid_feedback_min.append('<p>Необходимо указать минимальное значение шкалы.</p>');
                }
                if (max_val === '') {
                    if (!max_val_field.hasClass('is-invalid')) {
                        max_val_field.addClass('is-invalid');
                    }
                    invalid_feedback_max.append('<p>Необходимо указать максимальное значение шкалы.</p>');
                }
                if (step === '') {
                    if (!step_field.hasClass('is-invalid')) {
                        step_field.addClass('is-invalid');
                    }
                    invalid_feedback_step.append('<p>Необходимо указать шаг шкалы.</p>');
                }
            }
        } else if (scale_type === 'interval-scale') {
            values_fields.each(function (i, e) {
                let feedback = $('#invalid-feedback-' + old_scale_name + '-' + i);
                let value = $(e).val();
                if (value === '') {
                    if (!$(e).hasClass('is-invalid')) {
                        $(e).addClass('is-invalid')
                    }
                    feedback.append('<p>Необходимо заполнить пустое поле.</p>');
                } else {
                    if (!/^-?\d+([.,]\d+)?([eE][+-]\d+)?$/.test(value)) {
                        if (!$(e).hasClass('is-invalid')) {
                            $(e).addClass('is-invalid')
                        }
                        feedback.append('<p>Неверный формат поля.</p>');
                    }
                }
            });
        } else {
            modal_body.insertBefore(
                '<div class="alert alert-danger" role="alert" id="msg-' + old_scale_name + '-type-none">' +
                    'Необходимо выбрать тип шкалы.' +
                '</div>'
            );
        }
    } else {
        scale_name_field.removeClass('is-valid');
        if (!scale_name_field.hasClass('is-invalid')) {
            scale_name_field.addClass('is-invalid');
        }
        invalid_feedback_name.append('<p>Необходимо указать валидное название шкалы.</p>');
    }

    let is_valid = !scale_name_field.hasClass('is-invalid') &&
        msg.length === 0 &&
        !min_val_field.hasClass('is-invalid') &&
        !max_val_field.hasClass('is-invalid') &&
        !step_field.hasClass('is-invalid');
    values_fields.each(function (i, e) {
        if ($(e).hasClass('is-invalid')) {
            is_valid = false;
        }
    });

    if (is_valid) {
        $.ajax({
            dataType: "json",
            method: "POST",
            url: "/delete-scale/",
            data: {
                'scale-name': old_scale_name
            }
        }).done(function (response) {
            $.ajax({
                dataType: "html",
                method: "POST",
                url: "/add-scale/",
                data: {
                    'scale-name': scale_name,
                    'scale-type': scale_type,
                    'min-val': min_val,
                    'max-val': max_val,
                    'step': step,
                    'values': values
                }
            }).done(function (response) {
                $('#modal-' + old_scale_name).modal('hide');
                location.reload();
            }).fail(function (response) {
                console.log('1541');
                console.log(response);
            });
        }).fail(function (response) {
            console.log(response);
        });
    }
}

function delete_scale(scale_name) {
    let csrftoken = Cookies.get('csrftoken');
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
        url: "/delete-scale/",
        data: {
            'scale-name': scale_name
        }
    }).done(function (response) {
        location.reload();
    }).fail(function (response) {
        console.log(response);
    });
}

function delete_indicator(indicator_name) {
    let csrftoken = Cookies.get('csrftoken');
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
        url: "/delete-indicator/",
        data: {
            'indicator-name': indicator_name
        }
    }).done(function (response) {
        location.replace("?tab=indicators");
    }).fail(function (response) {
        console.log(response);
    });
}

function hide_indicator(indicator_name) {
    let csrftoken = Cookies.get('csrftoken');
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
        url: "/hide-indicator/",
        data: {
            'indicator-name': indicator_name
        }
    }).done(function (response) {
        location.replace("?tab=indicators");
    }).fail(function (response) {
        console.log(response);
    });
}

function show_indicator(indicator_name) {
    let csrftoken = Cookies.get('csrftoken');
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
        url: "/show-indicator/",
        data: {
            'indicator-name': indicator_name
        }
    }).done(function (response) {
        location.replace("?tab=indicators");
    }).fail(function (response) {
        console.log(response);
    });
}

function check_indicator_name(e) {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let indicator_name = $('#indicator-name-' + e.data.indicator_name);
    let indicator_name_val = indicator_name.val();
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/check-indicator-name/",
        data: {
            'indicator-name': indicator_name_val
        }
    }).done(function (response) {
        if (!response['res'] || e.data.indicator_name === indicator_name_val) {
            indicator_name.removeClass('is-invalid');
            if (indicator_name_val !== '') {
                indicator_name.addClass('is-valid');
            } else {
                indicator_name.removeClass('is-valid');
            }
        } else {
            indicator_name.removeClass('is-valid');
            if (indicator_name_val !== '') {
                indicator_name.addClass('is-invalid');
            } else {
                indicator_name.removeClass('is-invalid');
            }
        }
    }).fail(function (response) {
        console.log(response);
    });
}

function change_indicator(indicator_name) {
    $('#modal-indicator-' + indicator_name).modal('show');
}

function save_indicator(old_indicator_name) {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    let indicator_name_field = $('#indicator-name-' + old_indicator_name);
    let indicator_type_field = $('[name="indicator-type-' + old_indicator_name + '"]:checked');
    let indicator_show_field = $('#indicator-show-' + old_indicator_name);
    let indicator_description_field = $('#indicator-description-' + old_indicator_name);

    let invalid_feedback_name = $('#invalid-feedback-' + old_indicator_name + '-name');

    invalid_feedback_name.empty();

    let indicator_name =  indicator_name_field.val();
    let indicator_type =  indicator_type_field.val();
    let indicator_show =  indicator_show_field.val();
    let indicator_description =  indicator_description_field.val();

    let modal_body = $('#modal-indicator-' + old_indicator_name + ' .modal-body');
    let msg = $('[id^="msg-indicator-' + old_indicator_name + '-"]');
    msg.each(function (i, e) {
        $(e).delete();
    });
    let feedback = $('[id^="invalid-feedback-indicator-' + old_indicator_name + '-"]');
    feedback.each(function (i, e) {
        $(e).empty();
    });

    if (indicator_name !== '' && !indicator_name_field.hasClass('is-invalid')) {
        if (indicator_type === 'auto-indicator') {
        } else if (indicator_type === 'expert-indicator') {
        } else {
            modal_body.insertBefore(
                '<div class="alert alert-danger" role="alert" id="msg-indicator-' + old_indicator_name + '-type-none">' +
                    'Необходимо выбрать тип показателя.' +
                '</div>'
            );
        }
    } else {
        indicator_name_field.removeClass('is-valid');
        if (!indicator_name_field.hasClass('is-invalid')) {
            indicator_name_field.addClass('is-invalid');
        }
        invalid_feedback_name.append('<p>Необходимо указать валидное название показателя.</p>');
    }

    let is_valid = !indicator_name_field.hasClass('is-invalid') && msg.length === 0;

    if (is_valid) {
        $.ajax({
            dataType: "json",
            method: "POST",
            url: "/delete-indicator/",
            data: {
                'indicator-name': old_indicator_name
            }
        }).done(function (response) {
            $.ajax({
                dataType: "html",
                method: "POST",
                url: "/add-indicator/",
                data: {
                    'indicator-name': indicator_name,
                    'indicator-type': indicator_type,
                    'indicator-show': indicator_show,
                    'indicator-description': indicator_description
                }
            }).done(function (response) {
                $('#modal-indicator-' + old_indicator_name).modal('hide');
                location.reload();
            }).fail(function (response) {
                console.log(response);
            });
        }).fail(function (response) {
            console.log(response);
        });
    }
}