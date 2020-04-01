let year_selector = document.getElementById('selectYear');
let term_selector = document.getElementById('selectTerm');
let go_button = document.getElementById('gobtn');

function toggle_go_button() {
    if (year_selector.value != "" & term_selector.value != "") {
        new_location = `${window.location.pathname}${year_selector.value}/${term_selector.value}`
        go_button.href = new_location;
    } else {
        go_button.href = 'javascript:;';
    }
}

$(document).ready(function() {
    // Populates the years selection
    $.ajax({
        url: years_endpoint,
        success: function(data, textStatus, jqXHR) {
            for (var item in data) {
                var option = document.createElement('option');
                option.value = data[item];
                option.innerHTML = data[item];
                year_selector.appendChild(option);
            }
            toggle_go_button();
        },
    });

    // Populates the years selection
    $.ajax({
        url: terms_endpoint,
        success: function(data, textStatus, jqXHR) {
            for (var item in data) {
                var option = document.createElement('option');
                option.value = data[item];
                option.innerHTML = data[item];
                term_selector.appendChild(option);
            }
            toggle_go_button();
        },
    });

    // Add event listener to year selection change
    year_selector.addEventListener("change", function() {
        toggle_go_button();
    });

    // Add event listener to term selection change
    term_selector.addEventListener("change", function() {
        toggle_go_button();
    });
});