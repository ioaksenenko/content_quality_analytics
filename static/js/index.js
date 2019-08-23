$(document).ready(function () {
    let zip_file = $('#zip-file');
    let html_files = $('#html-files');

    zip_file.on('change',{file: html_files}, disable_file);
    html_files.on('change',{file: zip_file}, disable_file);

    disable_file({target: zip_file.get(0), data: {file: html_files}});
    disable_file({target: html_files.get(0), data: {file: zip_file}});
});


function disable_file(e) {
    if (e.target.files.length !== 0) {
        e.data.file.attr('disabled', 'true');
    } else {
        e.data.file.removeAttr('disabled');
    }
}