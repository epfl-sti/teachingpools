tinymce.init({
    selector: '#Message',
    skin: 'bootstrap',
    plugins: 'lists,link,preview',
    toolbar: 'h1 h2 bold italic strikethrough blockquote bullist numlist backcolor | link | preview',
    menubar: true,
    setup: function(editor) {
        editor.on('change', function() {
            tinymce.triggerSave();
        })
    },
});

// Set the datetime picker to now
$("#DoNotSendBefore").val(moment(Date.now()).format('DD.MM.YYYY HH:mm'));


// check documentation at https://www.malot.fr/bootstrap-datetimepicker/demo.php
$("#DoNotSendBefore").datetimepicker({
    format: "dd.mm.yyyy hh:ii",
    todayBtn: true,
    todayHighlight: true,
    weekStart: 1,
    autoclose: true,
    minuteStep: 15,
});

function toggleSpinner() {
    var el = document.getElementById("loading_spinner");
    if (el.style.display === "none") {
        el.style.display = "inline-block";
    } else {
        el.style.display = "none";
    }
}

$('#form').on('submit', function(e) {
    toggleSpinner();

    e.preventDefault();

    $.ajax({
        type: "POST",
        url: post_url,
        data: {
            to: $('#ToAddresses').val(),
            subject: $('#Subject').val(),
            message: $('#Message').val(),
            doNotSendBefore: $('#DoNotSendBefore').val(),
            csrfmiddlewaretoken: csrf_token,
            datatype: "json"
        },

        success: function(data) {
            window.location.href = success_redirect_url;
        },

        error: function(jqXHR, textStatus, errorThrown) {
            toggleSpinner();
            $("#output").html(`<div class="alert alert-danger" role="alert">Unable to process request (${jqXHR.status} - ${jqXHR.statusText}).</div>`);
        }
    });
})