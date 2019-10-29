/************** click anywhere on page to cancel popups **************/
$(document).click(function (e) {
    var container = $(".popup");
    // if the target of the click isn't the container nor a descendant of the container.
    if (!$(".more_vert").is(e.target) && container.has(e.target).length === 0) {
        container.attr('hidden', true);
    }
});

var this_url;
var this_comment;
var comment_id;
var hidden_comment;
var reported_comment;

/************** opens flag dialog that contains flag form **************/

$('.open_flag_dialog').click(function () {
    // get comment id of this event
    comment_id = $(this).attr('data-commentid');
    // identify this comment and its url
    this_comment = $('#cmt_thread_' + comment_id);
    this_url = $(this).attr('data-url');

    reported_comment = $('#reported_cmt_' + comment_id);

    // hide all current popups
    $('.popup').attr('hidden', true);
    $('#flag_form_container').attr('hidden', false);

});

/************** hide popup form and reset its text. **************/
function cancel_form() {
    $('#flag_form').trigger('reset');
    $('.popup').attr('hidden', true);
}

/************** toggles more button: shows/hides popup menu **************/
$('.more_vert').click(function () {
    var hidden = $(this).siblings('.popup').attr('hidden');
    $('.popup').attr('hidden', true);
    $(this).siblings('.popup').attr('hidden', !hidden);
});

// points to the comment that has been flagged/hidden
$('.async_hide').click(function (e) {
    e.preventDefault();

    // get comment id of this event
    comment_id = $(this).attr('data-commentid');
    // identify this comment, its url and its hidden comment
    this_comment = $('#cmt_thread_' + comment_id);
    this_url = $(this).attr('href');
    hidden_comment = $('#hidden_cmt_' + comment_id);

    $.ajax({
        type: 'POST',
        url: this_url,
        success: function (data) {
            console.log("submit successful!");
            if (this_comment != null) {
                this_comment.attr('hidden', true);
                hidden_comment.attr('hidden', false);
            }
        },
        error: function (data) {
            alert("An error has occurred, please resubmit report.");
        },
    })
});

/************** show hidden comments **************/
$('.async_unhide').click(function (e) {
    e.preventDefault();

    // get comment id of this event
    comment_id = $(this).attr('data-commentid');
    // identify this comment, its url and its hidden comment
    this_comment = $('#cmt_thread_' + comment_id);
    this_url = $(this).attr('href');
    hidden_comment = $('#hidden_cmt_' + comment_id);

    $.ajax({
        type: 'GET',
        url: this_url,
        success: function (data) {
            console.log("submit successful!");
            if (this_comment != null) {
                hidden_comment.attr('hidden', true);
                this_comment.attr('hidden', false);
            }
        },
        error: function (data) {
            alert("An error has occurred, please resubmit report.");
        },
    })
});

/************** click to show reported comment **************/
$('.async_unreport').click(function (e) {
    e.preventDefault();

    // get comment id of this event
    comment_id = $(this).attr('data-commentid');
    // identify this comment, its url and its hidden comment
    this_comment = $('#cmt_thread_' + comment_id);
    this_url = $(this).attr('href');
    reported_comment = $('#reported_cmt_' + comment_id);

    $.ajax({
        type: 'GET',
        url: this_url,
        success: function (data) {
            if (this_comment != null) {
                reported_comment.attr('hidden', true);
                this_comment.attr('hidden', false);
            }
        },
        error: function (data) {
            alert('Request failed.')
        }
    })
});

/************** sending ajax post request with flag forms **************/
var form = $('#flag_form');
form.submit(function (e) {
    e.preventDefault();

    $('.popup').attr('hidden', true);
    // open loader
    $('#loader').attr('hidden', false);

    if (this_url != null) {
        $.ajax({
            type: 'POST',
            url: this_url,
            data: form.serialize(),
            success: function (data) {
                console.log("submit successful!");
                if (this_comment != null) {
                    this_comment.attr('hidden', true);
                    reported_comment.attr('hidden', false);
                }
                form.trigger('reset');
                // close loader
                $('#loader').attr('hidden', true);
                $('#flag_response').attr('hidden', false);
            },
            error: function (data) {
                $('#loader').attr('hidden', true);
                alert("Request failed.");
            },

        })
    } else {
        alert("Undefined comment id.");
    }
});