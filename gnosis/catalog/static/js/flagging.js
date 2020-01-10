var $this_url;
var $this_comment;
var comment_id;

/************** opens flag dialog that contains flag form **************/

$('.open_flag_dialog').click(function () {
    if ($(this).has('.not_flagged').length) {
        // get comment id of this event
        comment_id = $(this).attr('data-commentid');
        $this_comment = $('#cmt_thread_' + comment_id);
        $this_url = $(this).attr('data-url');

        // hide all current popups
        $('.popup').attr('hidden', true);
        $('#flag_form_container').attr('hidden', false);
    }
});

$('#report_error').click(function () {
    $this_url = $(this).attr('data-url');
    // hide all current popups
    $('.popup').attr('hidden', true);
    $('#error_form_container').attr('hidden', false);
});

/************** hide popup form and reset its text. **************/
function cancel_form(form) {
    $('#' + form).trigger('reset');
    $('.popup').attr('hidden', true);
}

$('#flag_cancel_button').click(function () {
    cancel_form("flag_form");
});

$('#error_cancel_button').click(function () {
    cancel_form("error_form");
});


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
                        $this_comment.find('.comment_text').replaceWith('<p>Comment is being held for moderation</p>');
                        $this_comment.find('.material-icons').text('flag');
                        $this_comment.find('.not_flagged').attr('class', 'flagged').attr('title', 'Flagged');
                    }
                    form.trigger('reset');
                    // close loader
                    $('#loader').attr('hidden', true);
                    $('#response_text').text('Thanks. We have received your report. If we find this content to be in violation of our guidelines,\n' +
                        ' we will remove it.');
                    $('#response_msg').attr('hidden', false);
                } else {
                    alert("Invalid form.");
                    $('#loader').attr('hidden', true);
                }
            },
            error: function (data) {
                $('#loader').attr('hidden', true);
                alert("Request failed.");
            },

        })
    } else {
        alert("Undefined comment id. Please refresh.");
    }
});

form = $('#error_form');
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
                    form.trigger('reset');
                    // close loader
                    $('#loader').attr('hidden', true);
                    $('#response_text').text('Thanks. We have received your report.');
                    $('#response_msg').attr('hidden', false);
                } else {
                    alert("Invalid form.");
                    $('#loader').attr('hidden', true);
                }
            },
            error: function (data) {
                $('#loader').attr('hidden', true);
                alert("Request failed.");
            },

        })
    } else {
        alert('unidentified paper. Please refresh')
    }
});

// remove response message by clicking on ok button
$('.response_ok').click(function () {
    $('#response_msg').attr('hidden', true)
});

