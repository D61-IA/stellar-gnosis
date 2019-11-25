/************** click anywhere on page to cancel popups **************/
$(document).click(function (e) {
    var $container = $(".popup");
    var $target = $(".open_flag_dialog");
    // if the target of the click isn't the container nor a descendant of the container.
    if (!$target.is(e.target) && $target.has(e.target).length === 0 && $container.has(e.target).length === 0) {
        $container.attr('hidden', true);
    }
});

var $this_url;
var $this_comment;
var comment_id;

/************** opens flag dialog that contains flag form **************/

$('.open_flag_dialog').click(function () {
    if ($(this).attr('data-flagged') !== "True") {
        // get comment id of this event
        comment_id = $(this).attr('data-commentid');
        $this_comment = $('#cmt_thread_' + comment_id);
        $this_url = $(this).attr('data-url');

        // hide all current popups
        $('.popup').attr('hidden', true);
        $('#flag_form_container').attr('hidden', false);
    }
});

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

    if ($this_url != null) {
        $.ajax({
            type: 'POST',
            url: $this_url,
            data: form.serialize(),
            success: function (data) {
                console.log("submit successful!");
                if (data.is_valid) {
                    if ($this_comment != null) {
                        $this_comment.find('.comment_text').text('Comment is being held for moderation');
                        $this_comment.find('.material-icons').text('flag');
                        $this_comment.find('.with_cursor').attr('class', 'no_cursor').attr('title', 'Flagged');
                    }
                    form.trigger('reset');
                    // close loader
                    $('#loader').attr('hidden', true);
                    $('#flag_response').attr('hidden', false);
                } else {
                    alert("Invalid form.")
                }
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