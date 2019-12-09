$(document).ready(function () {
    $('#expert-analysis').submit(function () {
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

    dynamic_nav();
});


function show_tooltip() {
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

function dynamic_nav() {
    let nav = $('#modules-tabs');
    let height = nav.innerHeight();
    let dropdown_items = $('.dropdown-item');
    let n = dropdown_items.length;
    dropdown_items.each(function (i, e) {
        console.log(nav.innerHeight());
        console.log(height);
        if (nav.innerHeight() === height) {
            $(e).removeClass('dropdown-item');
            $(e).addClass('nav-link');
            nav.append($('<li class="nav-item"></li>').append($(e)));
            n--;
        } else {
            let dropdown_menu = $('.dropdown-menu');
            let nav_item = nav.find('li:last-child');
            let nav_link = nav_item.find('.nav-link');
            nav_link.removeClass('nav-link');
            nav_link.addClass('dropdown-item');
            dropdown_menu.prepend(nav_link);
            nav_item.detach();
            n++;
            return false;
        }
    });
    let dropdown = $('.dropdown');
    if (n === 0) {
        dropdown.detach();
        console.log('dsfsd');
    }
    nav.append(dropdown);

    let dropdown_dividers = $('.dropdown-divider');
    dropdown_dividers.each(function (i, e) {
        let prev = $(e).prev();
        let next = $(e).next();
        if (prev.length === 0 || next.length === 0 || prev.hasClass('dropdown-divider') || next.hasClass('dropdown-divider')) {
            $(e).detach();
        }
    });
}