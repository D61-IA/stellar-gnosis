var $this_action;
var $msg;

$('.mod_del').click(function (e) {
    e.preventDefault();
    $this_action = $('#actions_' + $(this).attr('data-id'));
    $msg = $('<div class="del_msg"><span>Deleted</span></div>');
    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            if (data.is_valid) {
                console.log("delete action success");
                $this_action.attr('hidden', true);
                $msg.insertAfter(
                    $this_action
                )
            } else {
                console.log("delete action fail")
            }
        }
    });
});

$('.mod_res').click(function (e) {
    e.preventDefault();
    $this_action = $('#actions_' + $(this).attr('data-id'));
    $msg = $('<div class="res_msg"><span>Restored</span></div>');
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