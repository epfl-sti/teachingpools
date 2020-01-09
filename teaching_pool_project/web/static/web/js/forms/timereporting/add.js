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

// function checkRequiredFields(chosenType) {
//     fields = $('form#form :input[data-tab]');
//     fields.each(function() {
//         if ($(this).attr('data-tab') == chosenType) {
//             if (((/true/i).test($(this).attr('data-required')))) {
//                 $(this).prop('required', true);
//             } else {
//                 $(this).prop('required', false);
//             }
//         } else {
//             // the field is not part of the current choice and should not be managed
//             console.log($(this).attr('data-tab'));
//         }

//         // reset the validation for the field
//         $(this).parsley().reset();
//     });
// }

$(document).ready(function() {
    /* Hide all the tabs except the 'Common' one */
    // Get the id of the currently selected activity type radio
    var selected_activity_type = $('input[type=radio][name=activity_type]:checked')[0].id;
    var tab_name = $('label[for="' + selected_activity_type + '"]')[0].innerText;
    toggleTabs(tab_name, activate_tab = false);

    $('input[type=radio][name=activity_type]').change(function() {
        var tab_name = this.labels[0].innerText;
        toggleTabs(tab_name, activate_tab = true);

        //        // handle custom validation because of type change
        //        checkRequiredFields(tab_name);
    });

    //    // Validation related stuff
    //    // create a custom validation for the years input
    //    window.Parsley
    //        .addValidator('consecutiveYears', {
    //            requirementType: 'string',
    //            validateString: function(value, requirement) {
    //                let re = /(\d{4})-(\d{4})/;
    //                let result = value.match(re);
    //
    //                // first quick test to make sure that the value matches the expected structure
    //                if (!Array.isArray(result)) {
    //                    return false;
    //                } else {
    //                    // simple test
    //                    if (result.length != 3) {
    //                        return false;
    //                    } else {
    //
    //                        // Test if the two year are consecutive
    //                        let first_year = parseInt(result[1]);
    //                        let second_year = parseInt(result[2]);
    //                        if (second_year == (first_year + 1)) {
    //                            return true;
    //                        } else {
    //                            return false;
    //                        }
    //                    }
    //                }
    //            },
    //            messages: {
    //                en: "This value must represent two consecutive years separated by a dash (e.g. 2019-2020)"
    //            }
    //        });
    //
    //    // activate the validation
    //    var form = $("#form").parsley();

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