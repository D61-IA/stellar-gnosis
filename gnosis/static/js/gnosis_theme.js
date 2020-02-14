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

$('#universal_select').change(function () {
    var $option = $('option:selected', this);
    var url = $option.attr('data-url');
    $('#universal_search').attr('action', url);
});


/************** click anywhere on page to cancel popups **************/
$('.cover').click(function (e) {
    var $container = $(".popup");

    // if the target of the click isn't the container nor a descendant of the container.
    $container.attr('hidden', true);
    $('.cover').attr('hidden', true);
});

$('.popup_opener').click(function () {
    var targetid = $(this).attr('data-targetid');
    var formid = $(this).attr('data-formid');

    if (formid !== null){
        $('#' + formid).attr('action', $(this).attr('data-url'));
    }
    $('#' + targetid).attr('hidden', false);
    $('.cover').attr('hidden', false);
});

$('.response_ok').click(function () {
    $('.popup').attr('hidden', true);
    $('.cover').attr('hidden', true);
});

$('.cancel_button').click(function () {
    var targetid = $(this).attr('data-targetid');
    $('#' + targetid).trigger('reset');
    $('.reaction').children().attr('hidden', true);

    $('.popup').attr('hidden', true);
    $('.cover').attr('hidden', true);
});
