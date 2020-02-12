var $universal_select = $('#universal_select');
var option_name = 'option[value="' + $universal_select.attr('data-type') + '"]';
var $option = $(option_name);
$option.attr('selected', 'selected');
$('#universal_search').attr('action', $option.attr('data-url'));

/************** JS functions that apply to elements in gnosis_theme.html **************/
$('.cus_toggle').click(function (e) {
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

$('.response_ok').click(function () {
    $('#flag_response').attr('hidden', true)
});

$universal_select.change(function () {
    var $option = $('option:selected', this);
    var url = $option.attr('data-url');
    $('#universal_search').attr('action', url);
});

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
$('.cus_toggle').click(function (e) {
    e.stopPropagation();
    $('#cus-dropdown').slideToggle(100);
});

/************** click anywhere on page to cancel popups **************/
// the popup object must contain the class popup, the object the triggers the popup must have class popup_opener
$(document).click(function (e) {
    var $container = $(".popup");
    // element that triggers popup
    var $target = $(".popup_opener");
    // if the target of the click isn't the container nor a descendant of the container.
    if (!$target.is(e.target) && $target.has(e.target).length === 0 && $container.has(e.target).length === 0) {
        $container.attr('hidden', true);
    }
});

$('.response_ok').click(function () {
    $('#response_msg').attr('hidden', true)
});