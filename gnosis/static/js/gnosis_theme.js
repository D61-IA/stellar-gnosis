// jQuery plugin to prevent double submission of forms
// src: https://stackoverflow.com/questions/2830542/prevent-double-submission-of-forms-in-jquery
jQuery.fn.preventDoubleSubmission = function () {
    $(this).on('submit', function (e) {
        var $form = $(this);

        if ($form.data('submitted')) {
            // Previously submitted - don't submit again
            e.preventDefault();
        } else {
            // Mark it so that the next submit can be ignored
            $form.data('submitted', true);
        }
    });

    // Keep chainability
    return this;
};

$('form').preventDoubleSubmission();

// apply loader to all ajax forms
// var form = $(document);
//
// $(document).ajaxStart(function () {
//     console.log("job starts!");
//     $('#loader').attr('hidden', false);
// });
//
//
// $(document).ajaxStop(function () {
//     console.log("job ends!");
//     $('#loader').attr('hidden', true);
//
// });