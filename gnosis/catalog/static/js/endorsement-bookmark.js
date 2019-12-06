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
                $that.attr({title: 'remove endorsement', class: "material-icons light_on"});
            } else {
                $that.html('lightbulb_outline');
                $that.attr({title: 'add endorsement', class: "material-icons light_off"});
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
                $that.attr({title: 'remove bookmark', class: "material-icons bm_on"});

            } else {
                $that.html('bookmark_border');
                $that.attr({title: 'add bookmark', class: "material-icons bm_off"});
            }
            console.log("bookmark action performed:", data.result)

        },
        error: function (data) {
            alert("An error has occurred, please resubmit report.");
        },
    })

});