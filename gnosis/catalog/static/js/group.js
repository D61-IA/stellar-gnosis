var $date_input = $('#id_date_discussed');
var $container = $('#discuss_form_container');
var meet_day = $container.attr('data-clubday');
var this_url;

$date_input.attr('autocomplete', 'off').datepicker({
    onSelect: function (date) {
        var curDate = $(this).datepicker('getDate');
        var dayName = $.datepicker.formatDate('DD', curDate);
        $('.reaction_message').attr('hidden', meet_day === dayName);
        $('.form_buttons').attr('hidden', false)
    },
    duration: 100
});

$date_input.css({
    'border-radius': 0,
});

$('#pick_date').css({
    'height': $date_input.css('height'),
}).click(function (e) {
    $date_input.datepicker('show');
    e.preventDefault();
});

$('.discuss_btn').click(function (e) {
    e.preventDefault();
    $container.attr('hidden', false);
    this_url = $(this).attr('href');
    $('#discuss_form').attr('action', this_url);
});