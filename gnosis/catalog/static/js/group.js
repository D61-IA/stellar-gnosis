var $date_input = $('#id_date_discussed');
var $container = $('#discuss_form_container');
var meet_day = $container.attr('data-clubday');
var this_url;

$('label[for="id_date_discussed"]').css('margin-right', '18px');

$date_input.attr('autocomplete', 'off').datepicker({
    onSelect: function (date) {
        var curDate = $(this).datepicker('getDate');
        var dayName = $.datepicker.formatDate('DD', curDate);
        if (meet_day !== dayName) {
            alert('Reminder: selected date does not match club meeting day.');
            // $('.date_alert').attr('hidden', false);
        }
    },
    duration: 100
});
$date_input.css({
    'border-radius': 0,
});
$('#pick_date').css({
    'height': $date_input.css('height'),
});
$(function () {
    $('#pick_date').click(function (e) {
        $date_input.datepicker('show');
        e.preventDefault();
    });
});

$('.discuss_btn').click(function (e) {
    e.preventDefault();
    $container.attr('hidden', false);
    this_url = $(this).attr('href');
    $('#discuss_form').attr('action', this_url);
});


// $('#discuss_form').submit(function(e){
//     e.preventDefault();
//
//     $.ajax({
//         type: 'POST',
//         url: this_url,
//         data: form.serialize(),
//         success: function(data){
//             console.log("submit successful");
//             if (data.is_valid){
//
//             }else {
//
//             }
//         },
//         error: function (data) {
//
//         }
//     })
//
// });