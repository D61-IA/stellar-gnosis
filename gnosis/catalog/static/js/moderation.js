var $this_action;
$('.mod_del').click(function (e) {
    e.preventDefault();
    $this_action = $('#actions_' + $(this).attr('data-id'));
    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            if (data.is_valid) {
                console.log("delete action success");
                $this_action.remove();
            } else {
                console.log("delete action fail")
            }
        }
    });
});

$('.mod_res').click(function (e) {
    e.preventDefault();
    $this_action = $('#actions_' + $(this).attr('data-id'));
    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            if (data.is_valid) {
                console.log("restore action success");
                $this_action.remove()
            } else {
                console.log("restore action fail")
            }
        }

    });
});