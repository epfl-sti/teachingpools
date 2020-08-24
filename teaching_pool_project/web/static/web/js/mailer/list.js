var el = document.getElementsByClassName('DT');
for (i = 0; i < el.length; i++) {
    el[i].innerHTML = moment(el[i].innerHTML).fromNow();
}

$('#previewModal').on('show.bs.modal', function(event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var id = button.data('id') // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var modal = $(this)
    modal.find('.modal-title').text('Preview of campaign ' + id)
    let content = '--> Test <--' + id;

    $.ajax({
        type: "POST",
        url: post_url,
        data: {
            id: id,
            csrfmiddlewaretoken: csrf_token,
            datatype: "json"
        },

        success: function(data) {
            document.getElementById('previewContent').innerHTML = data.msg;
        },

        error: function(jqXHR, textStatus, errorThrown) {
            document.getElementById('previewContent').innerHTML = `Unable to process request (${jqXHR.status} - ${jqXHR.statusText}).`;
        }
    });
});

$('#exampleModal').on('show.bs.modal', function(event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var id = button.data('id') // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var modal = $(this);
    var confirm_button = modal.find(".button-confirm");
    confirm_button.data('id', id);
    $(confirm_button).on("click", function() {
        var id = $(this).data("id");
        $.ajax({
            type: "POST",
            url: delete_url,
            data: {
                id: id,
                csrfmiddlewaretoken: csrf_token,
                datatype: "json"
            },

            success: function(data) {
                window.location.href = data.destination;
            },

            error: function(jqXHR, textStatus, errorThrown) {
                console.log(`Unable to process request (${jqXHR.status} - ${jqXHR.statusText}).`);
            }
        });
    })
});