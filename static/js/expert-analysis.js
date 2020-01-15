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

    let collapse = $('a[data-toggle="collapse"]');
    let collapse_show = $('a[data-toggle="collapse"][aria-expanded="true"]');
    let collapse_hide = $('a[data-toggle="collapse"][aria-expanded="false"]');

    /*collapse_show.each(function (i, e) {
        $(e).find(">:first-child").prepend('<span class="show mr-3"><i class="fas fa-angle-down"></i></span>');
        $(e).find(">:first-child").prepend('<span class="hide d-none mr-3"><i class="fas fa-angle-right"></i></span>');
    });

    collapse_hide.each(function (i, e) {
        $(e).find(">:first-child").prepend('<span class="show d-none mr-3"><i class="fas fa-angle-down"></i></span>');
        $(e).find(">:first-child").prepend('<span class="hide mr-3"><i class="fas fa-angle-right"></i></span>');
    });*/

    collapse.each(function (i, e) {
        let collapse = $($(e).attr('href'));
        collapse.on('hidden.bs.collapse', function () {
            let trigger = $('a[data-toggle="collapse"][aria-expanded="false"][href="#'+$(this).attr('id')+'"]');
            trigger.find('.hide').removeClass('d-none');
            trigger.find('.show').addClass('d-none');
        });
        collapse.on('shown.bs.collapse', function () {
            let trigger = $('a[data-toggle="collapse"][aria-expanded="true"][href="#'+$(this).attr('id')+'"]');
            trigger.find('.show').removeClass('d-none');
            trigger.find('.hide').addClass('d-none');
        });
    });

    dynamic_nav();

    let tabs = $('span[data-toggle="tooltip"]');
    tabs.each(function (i, e) {
        $(e).tooltip();
    });

    $('[type="checkbox"][id$="-webinar-has-scenario"]').change(function () {
        if (this.checked) {
            $('#scenario-block').removeClass('d-none');
        } else {
           $('#scenario-block').addClass('d-none');
        }
    });

    $('[type="checkbox"][id$="-webinar-has-presentation"]').change(function () {
        if (this.checked) {
            $('#presentation-block').removeClass('d-none');
        } else {
           $('#presentation-block').addClass('d-none');
        }
    });

    $('[type="checkbox"][id$="-webinar-has-additional-materials"]').change(function () {
        if (this.checked) {
            $('#additional-materials-block').removeClass('d-none');
        } else {
           $('#additional-materials-block').addClass('d-none');
        }
    });

    $('[type="checkbox"][id$="-webinar-has-questions"]').change(function () {
        if (this.checked) {
            $('#questions-block').removeClass('d-none');
        } else {
           $('#questions-block').addClass('d-none');
        }
    });
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
    let dropdown = $('.dropdown');
    dropdown_items.each(function (i, e) {
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
            nav.append(dropdown);
            n++;
            return false;
        }
    });
    if (n === 0) {
        dropdown.detach();
    }

    let dropdown_dividers = $('.dropdown-divider');
    dropdown_dividers.each(function (i, e) {
        let prev = $(e).prev();
        let next = $(e).next();
        if (prev.length === 0 || next.length === 0 || prev.hasClass('dropdown-divider') || next.hasClass('dropdown-divider')) {
            $(e).detach();
        }
    });
}