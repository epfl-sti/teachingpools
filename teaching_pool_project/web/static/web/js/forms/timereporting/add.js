function toggleTabs(tab_to_keep, activate_tab = true) {
    var all_tabs = $('form>ul.nav-tabs>li.nav-item');
    all_tabs.each(function() {
        if (this.innerText != tab_to_keep & this.innerText != "Common") {
            $(this).hide();
        } else {
            $(this).show();
            if (activate_tab & this.innerText == tab_to_keep) {
                $(this).find("a").trigger("click");
            }
        }
    });
}

$(document).ready(function() {
    /* Hide all the tabs except the 'Common' one */
    // Get the id of the currently selected activity type radio
    var selected_activity_type = $('input[type=radio][name=activity_type]:checked')[0].id;
    var tab_name = $('label[for="' + selected_activity_type + '"]')[0].innerText;
    toggleTabs(tab_name, activate_tab = false);

    $('input[type=radio][name=activity_type]').change(function() {
        var tab_name = this.labels[0].innerText;
        toggleTabs(tab_name, activate_tab = true);
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