var $this_comment;

$('.icon_button').click(function (e) {
    $this_comment = $('#comment_' + $(this).attr('data-commentid'));
});

/************** sending ajax post request with flag forms **************/
var form = $('#flag_form');
form.submit(function (e) {
    e.preventDefault();

    $('.popup').attr('hidden', true);
    // open loader
    $('#loader').attr('hidden', false);

    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: form.serialize(),
        success: function (data) {
            console.log("submit successful!");
            if (data.is_valid) {
                if ($this_comment != null) {
                    $this_comment.find('.comment_text').replaceWith('<p>Comment is being held for moderation</p>');
                    $this_comment.find('.icon_button').replaceWith('' +
                        '<a class="right_side_icon" data-toggle="tooltip"\n' +
                        'title="Flagged">\n' +
                        '<i class="material-icons menu_item">flag</i>\n' +
                        '</a>');
                }
                form.trigger('reset');
                // close loader
                $('#loader').attr('hidden', true);
                $('#flag_response').attr('hidden', false);
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
});

