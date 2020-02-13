var $date_input = $('#id_date_discussed');
var $container = $('#discuss_form_container');
var meet_day = $container.attr('data-clubday');

$date_input.attr('autocomplete', 'off').datepicker({
    onSelect: function (date) {
        var curDate = $(this).datepicker('getDate');
        var dayName = $.datepicker.formatDate('DD', curDate);
        $('.reaction_message').attr('hidden', meet_day === dayName);
        $('.form_buttons').attr('hidden', false)
    },
    duration: 100
});

$('#date_opener').css({
    'height': $date_input.css('height'),
}).click(function (e) {
    e.preventDefault();
    $date_input.datepicker('show');
});

$('.discuss_btn').click(function (e) {
    e.preventDefault();
    $container.attr('hidden', false);
    $('#discuss_form').attr('action', $(this).attr('href'));
});
