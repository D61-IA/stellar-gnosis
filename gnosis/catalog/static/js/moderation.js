var $this_action;
var $msg;
var $state;

$('.mod_del').click(function (e) {
    e.preventDefault();
    $this_action = $('#actions_' + $(this).attr('data-id'));
    $msg = $('<div class="del_msg"><span>Deleted</span></div>');
    $state = $('#state_' + $(this).attr('data-id'));

    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            if (data.is_valid) {
                console.log("delete action success");
                $this_action.attr('hidden', true);
                $state.attr('hidden', true);
                $msg.insertAfter(
                    $this_action
                )
            } else {
                console.log("delete action fail")
            }
        }
    });
});

$('.mod_rest').click(function (e) {
    e.preventDefault();
    $this_action = $('#actions_' + $(this).attr('data-id'));
    $msg = $('<span class="res_msg"><span>Restored</span></span>');
    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            if (data.is_valid) {
                console.log("restore action success");
                $this_action.attr('hidden', true);
                $msg.insertAfter(
                    $this_action
                )
            } else {
                console.log("restore action fail")
            }
        }

    });
});


$('.mod_resl').click(function (e) {
    e.preventDefault();
    var $this = $(this);
    $msg = $('#state_' + $this.attr('data-id') + ' span');

    $.ajax({
        type: 'POST',
        url: $this.attr('href'),
        success: function (data) {
            if (data.is_resolved) {
                console.log("Report marked resolved.");
                $this.text('Mark Unresolved');
                $msg.text("Resolved").attr('class', 'res_msg');
            } else if (data.is_resolved === false) {
                console.log("Report marked unresolved.");
                $this.text('Mark Resolved');
                $msg.text("Unresolved").attr('class', 'del_msg');
            } else {
                console.log('Undetermined resolve case.')
            }
        }

    });
});