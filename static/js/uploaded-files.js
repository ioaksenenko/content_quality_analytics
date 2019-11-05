$(document).ready(function () {
    let csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    let files_names = [];
    $('[id^="file-name-"]').each(function (i, e) {
        files_names.push($(e).text());
    });
    $.ajax({
        dataType: "json",
        method: "POST",
        url: "/restore-deleted-uploaded-files/",
        data: {
            'files-names': files_names
        }
    }).done(function (response) {
        console.log(response);
    }).fail(function (response) {
        console.log(response);
    });
});

function delete_file(file_name)
{
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
        url: "/delete-uploaded-file/",
        data: {
            'file-name': file_name
        }
    }).done(function (response) {
        if (response['redirect'] !== "") {
            location.replace(response['redirect'])
        } else {
            location.reload();
        }
    }).fail(function (response) {
        console.log(response);
    });
}