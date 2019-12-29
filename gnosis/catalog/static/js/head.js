function pagination(current, first, last) {

    var $page_items = $('.num_item');

    var path = '?page=';

    if (last > 5) {
        if (current <= first + 2) {
            $($page_items).each(function (index) {
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
            $($page_items).each(function (index) {
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
            $page_items.eq(0).children('a').text(first).attr('href', path + first);
            $page_items.eq(1).children('a').text((current - 1)).attr('href', path + (current - 1));
            $page_items.eq(2).children('a').text((current)).attr('href', path + (current));
            $page_items.eq(2).addClass('active');
            $page_items.eq(3).children('a').text((current + 1)).attr('href', path + (current + 1));
            $page_items.eq(4).children('a').text(last).attr('href', path + last);
        }

    } else {
        $($page_items).each(function (index) {
            if (index + 1 <= last) {
                $(this).children('a').text(index + 1).attr('href', path + (index+1));
                if (current === index + 1) {
                    $(this).addClass('active');
                }
            } else {
                $(this).css('display', 'none');
            }
        });
    }

    if (current <= first + 2) {
        $('.first_ellipsis').css('display', 'none');
    }

    if (current >= last - 2) {
        $('.last_ellipsis').css('display', 'none');
    }

}