// jQuery plugin to prevent double submission of forms
// src: https://stackoverflow.com/questions/2830542/prevent-double-submission-of-forms-in-jquery
jQuery.fn.preventDoubleSubmission = function () {
    $(this).on('submit', function (e) {
        var $form = $(this);

        if ($form.data('submitted')) {
            // Previously submitted - don't submit again
            e.preventDefault();
        } else {
            // Mark it so that the next submit can be ignored
            $form.data('submitted', true);
        }
    });

    // Keep chainability
    return this;
};

$('form').preventDoubleSubmission();

/************** Django basic setup for accepting ajax requests. **************/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

// Setup ajax connections safetly

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }
);

/************** JS functions that apply to elements in gnosis_theme.html **************/
$('.toggle-nav').click(function () {
    $('#nav-small-content .dropdown-menu').slideToggle(100);
});

$('.cus-toggle').click(function (e) {
    e.stopPropagation();
    $('#cus-dropdown').slideToggle(100);
});

/************** click anywhere on page to cancel popups **************/
$(document).click(function (e) {
    var $container = $(".popup");
    // element that triggers popup
    var $target = $(".popup_opener");
    // if the target of the click isn't the container nor a descendant of the container.
    if (!$target.is(e.target) && $target.has(e.target).length === 0 && $container.has(e.target).length === 0) {
        $container.attr('hidden', true);
    }
});