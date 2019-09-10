/* functions to control interactions between recaptcha and submit button */
var widget = "invisible";

function setWidget(w) {
    widget = w;
}

// if submit button id is not provided, it will use class 'captcha-submit instead.
// if recaptcha is checkbox, set it to disable.
function setButton(id) {
    var button_id = '.captcha-submit';

    if (id !== undefined) {
        button_id = '#' + id;
    }

    $(button_id).prop('disabled', false);

    if (widget === "checkbox"){
        $(button_id).prop('disabled', true);
    }
}

/* callback functions for when different errors happen at client side verification */
// when receive data (meaning client side verification is successful), allow submit button to work properly.
function dataCallback() {
    $('.captcha-submit').prop('disabled', false);
}

// the response token has 2 mins before it expires, when that happens, disable the submit button (requires to re-verify).
function dataExpiredCallback() {
    $('.captcha-submit').prop('disabled', true);
}

// if received connection error, use a pop up window to remind user to re-verify, also disables the submit button.
function dataErrorCallback() {
    $('.captcha-submit').prop('disabled', true);
    window.alert("Network connectivity error, please retry reCaptcha.")
}