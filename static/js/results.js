$(document).ready(function () {
    $('#results').submit(function () {
        let next = $('#next');
        let spinner = $('#spinner');

        next.prop('disabled', true);
        spinner.removeClass('d-none');
    });

    let ranges = $('[type="range"]');
    ranges.each(function (i, e) {
        $(e).tooltip();
        $(e).change(function () {
            $(this).tooltip('dispose');
            $(this).attr("title", $(this).val());
            $(this).tooltip();
        });
        $(e).hover(show_tooltip);
        $(e).click(show_tooltip);
        $(e).focus(show_tooltip);
    });
});

function show_tooltip()
{
    let element = $(this);
    element.tooltip('dispose');
    let min = element.attr('min');
    let max = element.attr('max');
    let step = element.attr('step');
    let val = element.val();
    let n = (max - min) / step;
    setTimeout(function () {
        let tooltip = $('#' + element.attr('aria-describedby'));
        let left = element.offset().left - tooltip.width() / 4;
        let right = element.offset().left + element.width() - tooltip.width() / 1.3;
        tooltip.offset({left: left + ((right - left) / n) * val });
    }, 1);
    $(this).tooltip('show');
}