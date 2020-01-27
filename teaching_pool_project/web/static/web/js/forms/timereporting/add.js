function toggleTabs(tab_to_keep, activate_tab = true) {
    var all_tabs = $('form>ul.nav-tabs>li.nav-item');
    all_tabs.each(function() {
        if (this.innerText.toLowerCase() != tab_to_keep.toLowerCase() & this.innerText.toLowerCase() != "common") {
            $(this).hide();
        } else {
            $(this).show();
            if (activate_tab & this.innerText.toLowerCase() == tab_to_keep.toLowerCase()) {
                $(this).find("a").trigger("click");
            }
        }
    });
}

$(document).ready(function() {
    // Use select2 on the dropdown that require it
    $('select[data-use-select2="true"]').each(function() {
        $(this).select2({
            theme: 'bootstrap4',
        });
    })

    /* Hide all the tabs except the 'Common' one */
    // Get the id of the currently selected activity type radio
    var selected_activity_type = $('input[type=radio][name=activity_type]:checked')[0].id;
    var tab_name = $('label[for="' + selected_activity_type + '"]')[0].innerText.replace(/[^a-z0-9\s]/gi, '').replace(/\r?\n|\r/g, '').trim();
    toggleTabs(tab_name, activate_tab = false);

    $('input[type=radio][name=activity_type]').change(function() {
        var tab_name = this.labels[0].innerText;
        toggleTabs(tab_name, activate_tab = true);
    });

    // Highlight the tabs containing validation errors
    $('span[class="invalid-feedback"], p[class="invalid-feedback"]').each(function() {
        let tabname = $(this).parents('.tab-pane').attr('id');
        let tabheader = $('a[data-toggle="tab"][href="#' + tabname + '"]')
        $(tabheader).css({ 'color': 'red', 'font-weight': 'bold' })
    });
});

// find all the elements that will be using the autocomplete
var el = $('input[data-autocomplete=true]');
$(el).each(function() {
    var endpoint = $(this).attr('data-autocomplete-source');
    $(this).autocomplete({
        source: $(this).attr('data-autocomplete-source'),
        minLength: 3,
        open: function() {
            setTimeout(function() {
                $('.ui-autocomplete').css('z-index', 99);
            }, 0);
        },
        select: function(event, ui) {
            console.log(ui.item.value);
        }
    });
});