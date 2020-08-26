var el = document.getElementsByClassName('DT');
for (i = 0; i < el.length; i++) {
    el[i].innerHTML = moment(el[i].innerHTML).fromNow();
}

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
                $("#exampleModal").modal('hide');

                var idx = null;
                applications_table.rows().every(function(rowIdx, tableLoop, rowLoop) {
                    var row_data = this.data();
                    if (row_data[0] === data.id) {
                        idx = rowIdx;
                    }
                });

                if (idx !== null) {
                    applications_table.rows(idx).remove();
                    applications_table.draw();
                }
            },

            error: function(jqXHR, textStatus, errorThrown) {
                console.log(`Unable to process request (${jqXHR.status} - ${jqXHR.statusText}).`);
            }
        });
    })
});

$(document).ready(function() {
    window.applications_table = $('#applications').DataTable({
        "columnDefs": [{
                "targets": [0],
                "visible": false,
                "searchable": false,
            },
            {
                "targets": [7],
                "orderable": false,
            },
            {
                "targets": [1, 4],
                "render": function(data, type, row, meta) {
                    if (data !== "") {
                        formatted_date = moment(data).format('lll');
                        rel_date = `<div class="text-muted">(${moment(data).fromNow()})</div>`;
                        return `${formatted_date} ${rel_date}`;
                    } else {
                        return '';
                    }
                }
            },
            {
                "targets": [6],
                "render": function(data, type, row, meta) {
                    switch (data) {
                        case "Pending":
                            return `<i class='far fa-hourglass'></i>&nbsp;${data}`;
                            break;
                        case "Hired":
                            return `<i class="far fa-thumbs-up"></i>&nbsp;${data}`;
                            break;
                        case "Rejected":
                            return `<i class="far fa-thumbs-down"></i>&nbsp;${data}`;
                            break;
                        case "Withdrawn":
                            return `<i class="fas fa-undo"></i>&nbsp;${data}`;
                            break;
                        default:
                            return data;
                    }
                }
            },
            {
                "targets": [2, 5],
                "render": function(data, type, row, meta) {
                    return type === 'display' && data.length > 20 ?
                        '<span title="' + data + '">' + data.substr(0, 18) + '...</span>' :
                        data;
                }
            },
        ],
        "rowCallback": function(row, data) {
            switch (data[6]) {
                case "Pending":
                    row.classList.add("table-primary");
                    break;
                case "Hired":
                    row.classList.add("table-success");
                    break;
                case "Rejected":
                    row.classList.add("table-danger");
                    break;
                case "Withdrawn":
                    row.classList.add("table-secondary");
                    break;
                default:
                    row.classList.add("table-secondary");
                    break;
            }
        },
        "order": [
            [1, 'desc'],
        ],
    });
});