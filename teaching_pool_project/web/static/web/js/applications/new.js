$(document).ready(function() {
    $('#output').hide();
});

$('#applicant').select2({
    ajax: {
        url: applicants_endpoint,
        dataType: 'json',
        processResults: function(data) {
            return {
                results: data.items
            };
        }
    }
});

$('#course').select2({
    ajax: {
        url: courses_endpoint,
        dataType: 'json',
        processResults: function(data) {
            return {
                results: data.items
            };
        }
    }
});

$('#status').select2({
    ajax: {
        url: status_endpoint,
        dataType: 'json',
        processResults: function(data) {
            return {
                results: data.items
            };
        }
    }
});

$('#form').on('submit', function(e) {
    e.preventDefault();

    var el_applicant = document.getElementById('applicant');
    var el_course = document.getElementById('course');
    var el_status = document.getElementById('status');

    $.ajax({
        type: "POST",
        url: post_endpoint,
        data: {
            applicant: el_applicant.options[el_applicant.selectedIndex].value,
            course: el_course.options[el_course.selectedIndex].value,
            status: el_status.options[el_status.selectedIndex].value,
            csrfmiddlewaretoken: csrf_token,
            datatype: "json"
        },

        success: function(data) {
            $("#output").html(data.msg);
            if (data.status === "ok") {
                document.getElementById("output").className = "alert alert-success alert-dismissible";
                $('#output').slideDown(500);
                setTimeout(function() {
                    $('#output').slideUp(500);
                }, 4000);
            } else {
                document.getElementById("output").className = "alert alert-danger";
                $("#output").show();
            }

        },

        error: function(jqXHR, textStatus, errorThrown) {
            $("#output").html(textStatus);
            document.getElementById("output").className = "alert alert-danger";
            $("#output").show();

        }
    });
})