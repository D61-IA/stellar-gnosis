function endorsement_bookmark_fun(id, div_id){
    console.log("success");
    var frm = $(id);
    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: {csrfmiddlewaretoken: window.CSRF_TOKEN},
            success: function () {
                $(div_id).load(" "+ div_id, endorsement_bookmark_fun());
            },
            error: function () {
                alert("something is wrong");
            }
        });
        return false;
    });
}
