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