$('#e_create').click(function (e) {
    e.preventDefault();
    var $that = $(this).children('.material-icons');
    // $(this) becomes undefined inside ajax function
    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            console.log("submit successful!");
            if (data.result === "add") {
                $that.html('lightbulb');
                $that.css('color', '#FFFF00');
            } else {
                $that.html('lightbulb_outline');
                $that.css('color', '#000000');
            }
            console.log("endorsement action performed:", data.result)

        },
        error: function (data) {
            alert("An error has occurred, please resubmit report.");
        },
    })
});

$('#b_create').click(function (e) {
    var $that = $(this).children('.material-icons');
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: $(this).attr('href'),
        success: function (data) {
            console.log("submit successful!");
            if (data.result === "add") {
                $that.html('bookmark');
            } else {
                $that.html('bookmark_border');
            }
            console.log("bookmark action performed:", data.result)

        },
        error: function (data) {
            alert("An error has occurred, please resubmit report.");
        },
    })

});