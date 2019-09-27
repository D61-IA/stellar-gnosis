/************** click anywhere on page to cancel popups **************/
$(document).click(function (e) {
    var container = $(".popup");
    // if the target of the click isn't the container nor a descendant of the container.
    if (!$(".more_vert").is(e.target) && container.has(e.target).length === 0) {
        container.attr('hidden', true);
    }
});

/************** toggles more button: shows/hides popup menu **************/
function toggle_more(ele) {
    var hidden = $(ele).siblings('.popup').attr('hidden');
    $('.popup').attr('hidden', true);
    $(ele).siblings('.popup').attr('hidden', !hidden);
}

/************** opens flag dialog that contains flag form **************/
function open_flag_dialog(comment_id) {
    // hide all current popups
    $('.popup').attr('hidden', true);
    $('#flag_form_container').attr('hidden', false);

    // add comment id to the form
    $("<input />").attr("type", "hidden")
        .attr("name", "comment_id")
        .attr("value", comment_id)
        .appendTo("#flag_form");
}

/************** hide popup form and reset its text. **************/
function cancel_form() {
    $('#flag_form').trigger('reset');
    $('.popup').attr('hidden', true);
}

/************** sending ajax post request with flag forms **************/
var form = $('#flag_form');
form.submit(function (e) {
    e.preventDefault();

    $('.popup').attr('hidden', true);

    // open loader
    $('#loader').attr('hidden', false);

    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: form.serialize(),
        success: function (data) {
            console.log("submit successful!");
            $('#flag_form').trigger('reset');
            // close loader
            $('#loader').attr('hidden', true);
            $('#flag_response').attr('hidden', false);
        },
        error: function (data) {
            $('#loader').attr('hidden', true);
            alert("An error has occurred, please resubmit report.");
        },

    })
});

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