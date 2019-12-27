function pagination(current, first, last) {

    if (current <= first + 2) {
        $('.first_ellipsis').css('display', 'none');
    }

    if (current >= last - 2) {
        $('.last_ellipsis').css('display', 'none');
    }
}