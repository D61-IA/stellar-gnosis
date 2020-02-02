function pagination($num_items, current, first, last, current_path) {
    var path = '?page=';

    if (current_path.indexOf('?keywords=') !== -1) {
        current_path = current_path.replace('&amp;', '&');
        var i = current_path.indexOf('&page=');
        if (i !== -1) {
            path = current_path.slice(0, i + 6)
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


function multi_pagination(pages) {
    // current, first, last, current_path
    var path = '?';
    var next_path = '';
    var page, class_name, $num_items, current, first, last, page_name, $first_ellipsis, $last_ellipsis;

    for (var k = 0; k < pages.length; k++) {
        page = pages[k];
        next_path += page.page_name + '=' + page.current + '&';
    }
    next_path = next_path.slice(0, -1);

    for (var i = 0; i < pages.length; i++) {
        page = pages[i];
        class_name = page.class_name;
        current = page.current;
        first = page.first;
        last = page.last;
        page_name = page.page_name;

        $num_items = $('.' + class_name + ' .pagination' + ' .num_item');
        $first_ellipsis = $('.' + class_name + ' .pagination' + ' .first_ellipsis');
        $last_ellipsis = $('.' + class_name + ' .pagination' + ' .last_ellipsis');

        // construct the path
        if (i !== 0) {
            path += '&' + page_name + '=';
        } else {
            path += page_name + '=';
        }

        var j = next_path.indexOf('&', 1);

        if (j === -1) {
            next_path = '';
        } else {
            next_path = next_path.substring(j);
        }

        if (last > 5) {
            if (current <= first + 2) {
                $($num_items).each(function (index) {
                    if (index === 4) {
                        $(this).children('a').text(last).attr('href', path + last + next_path);
                    } else {
                        $(this).children('a').text(index + 1).attr('href', path + (index + 1) + next_path);
                        if (current === index + 1) {
                            $(this).addClass('active');
                        }
                    }
                })
            } else if (current >= last - 2) {
                $($num_items).each(function (index) {
                    if (index === 0) {
                        $(this).children('a').text(first).attr('href', path + first + next_path);
                    } else {
                        $(this).children('a').text(last - 4 + index).attr('href', path + (last - 4 + index) + next_path);
                        if (current === last - 4 + index) {
                            $(this).addClass('active');
                        }
                    }
                })
            } else {
                $num_items.eq(2).addClass('active');
            }

            if (current <= first + 2) {
                $first_ellipsis.css('display', 'none');
            }

            if (current >= last - 2) {
                $last_ellipsis.css('display', 'none');
            }

        } else {
            $($num_items).each(function (index) {
                if (index + 1 <= last) {
                    $(this).children('a').text(index + 1).attr('href', path + (index + 1) + next_path);
                    if (current === index + 1) {
                        $(this).addClass('active');
                    }
                } else {
                    $(this).css('display', 'none');
                }
            });
            $first_ellipsis.css('display', 'none');
            $last_ellipsis.css('display', 'none');

        }
        path += current;
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

