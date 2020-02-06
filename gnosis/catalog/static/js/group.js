var dateToday = new Date();
var $date_alert = $('.date_alert');

var meetDay = $date_alert.attr('data-clubday');
$('#id_date_discussed').attr('autocomplete', 'off').datepicker({
    minDate: dateToday,
    onSelect: function (date) {
        var curDate = $(this).datepicker('getDate');
        var dayName = $.datepicker.formatDate('DD', curDate);
        if (meetDay !== dayName) {
            $('.date_alert').attr('hidden', false);
        }
    },
    duration: 100
});

$date_alert.find('.response_reset').click(function () {
    $('.cover').attr('hidden', true);
    $('#id_date_discussed').val('').datepicker("show");
});

$('.discuss_btn').click(function (e) {
    e.preventDefault();
    $('#discuss_form_container').attr('hidden', false)
});