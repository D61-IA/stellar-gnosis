function pagination($num_items, current, first, last, current_path) {
    var path = '?page=';

    if (current_path.indexOf('?keywords=') !== -1) {
        current_path = current_path.replace('&amp;', '&');
        var i = current_path.indexOf('&page=');
        if (i !== -1) {
            path = current_path.slice(0, i+6)
        } else {
            path = current_path;
            path += '&page=';
        }
    }

    if (last > 5) {
        if (current <= first + 2) {
            $($num_items).each(function (index) {
                if (index === 4) {
                    $(this).children('a').text(last).attr('href', path + last);
                } else {
                    $(this).children('a').text(index + 1).attr('href', path + (index + 1));
                    if (current === index + 1) {
                        $(this).addClass('active');
                    }
                }
            })
        } else if (current >= last - 2) {
            $($num_items).each(function (index) {
                if (index === 0) {
                    $(this).children('a').text(first).attr('href', path + first);
                } else {
                    $(this).children('a').text(last - 4 + index).attr('href', path + (last - 4 + index));
                    if (current === last - 4 + index) {
                        $(this).addClass('active');
                    }
                }
            })
        } else {
            $num_items.eq(2).addClass('active');
        }

        if (current <= first + 2) {
            $('.first_ellipsis').css('display', 'none');
        }

        if (current >= last - 2) {
            $('.last_ellipsis').css('display', 'none');
        }

    } else {
        $($num_items).each(function (index) {
            if (index + 1 <= last) {
                $(this).children('a').text(index + 1).attr('href', path + (index + 1));
                if (current === index + 1) {
                    $(this).addClass('active');
                }
            } else {
                $(this).css('display', 'none');
            }
        });
        $('.first_ellipsis').css('display', 'none');
        $('.last_ellipsis').css('display', 'none');

    }

    /************** hide/show elements depending on current display width **************/
    if ($(window).width() <= 678) {
        $('.mobile').css('display', '');
        $('.desktop').css('display', 'none');
    } else {
        $('.mobile').css('display', 'none');
        $('.desktop').css('display', '');
    }

    $(window).resize(function () {
        if ($(window).width() <= 678) {
            $('.mobile').css('display', '');
            $('.desktop').css('display', 'none');
        } else {
            $('.mobile').css('display', 'none');
            $('.desktop').css('display', '');
        }
    });
}
