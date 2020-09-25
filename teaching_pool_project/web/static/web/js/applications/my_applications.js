// bind the modal display with the correct application
$('#confirm-delete').on('show.bs.modal', function(e) {
    $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
})

// activate the tooltips
$(function() {
    $('[data-toggle="tooltip"]').tooltip();
})

const get_applications = async function() {
    const data = await (await fetch('.', {
        "headers": { "X-Requested-With": "XMLHttpRequest" },
    }).catch(handleErr)).json();
    if (data.code == 400) {
        return;
    }
    return data;
}

const get_template = async function() {
    try {
        const template_url = `${STATIC_URL}web/FE_templates/applications/my_applications_application_card.njk`;
        const data = await fetch(template_url).then(function(response) { return response.text(); });
        const env = nunjucks.configure(STATIC_URL, {
            autoescape: true,
            trimBlocks: true,
            lstripBlocks: true,
        });
        const template = nunjucks.compile(data, env);
        return template;


    } catch (err) {
        console.error(err);
        debugger;
    }
}

function handleErr(err) {
    console.warn(err);
    let resp = new Response(JSON.stringify({
        code: 400,
        message: "Bad request"
    }));
    return resp;
}

const buildOutput = function(applications, template, canWithdraw) {
    // DOM manipulation
    const root_node = document.getElementById('applications');

    const uniqueYears = Array.from(new Set(applications.map(item => item.year))).sort((a, b) => {
        a = a.toUpperCase();
        b = b.toUpperCase();
        if (a < b) {
            return 1;
        }
        if (a > b) { return -1; }
        return 0;
    });
    for (const year of uniqueYears) {
        // DOM manipulation
        const year_node = document.createElement("h4");
        const year_text = document.createTextNode(year);
        year_node.appendChild(year_text);
        year_node.classList.add("alert");
        year_node.classList.add("alert-info");
        root_node.appendChild(year_node);

        // get all the applications for the given year
        const this_year_applications = applications.filter(item => item.year === year);

        // get all the terms present in this list of applications
        const uniqueTerms = Array.from(new Set(this_year_applications.map(item => item.term))).sort((a, b) => {
            a = a.toUpperCase();
            b = b.toUpperCase();
            if (a < b) {
                return 1;
            }
            if (a > b) { return -1; }
            return 0;
        });

        for (const term of uniqueTerms) {
            // DOM manipulation
            var term_node = document.createElement("h5");
            var term_text = document.createTextNode(term);
            term_node.appendChild(term_text);
            term_node.classList.add("alert");
            term_node.classList.add("alert-primary");
            year_node.insertAdjacentElement("afterend", term_node)

            const this_term_applications = this_year_applications.filter(item => item.term === term);

            for (const application of this_term_applications) {
                const result = template.render({
                    application: application,
                    canWithdraw: canWithdraw
                });
                term_node.insertAdjacentHTML('afterend', result);
            }
        }
    }
}

const buildEmptyOutput = function() {
    const rootNode = document.getElementById('applications');
    const empty_applications_node = document.createElement("div");
    const empty_applications_text = document.createTextNode("You did not apply to any TA duty yet.");
    empty_applications_node.appendChild(empty_applications_text);
    empty_applications_node.classList.add("alert");
    empty_applications_node.classList.add("alert-info");
    rootNode.appendChild(empty_applications_node);
    return;
}

const main = async function() {
    const applications = await get_applications();
    if (applications.data.length > 0) {
        const template = await get_template();
        buildOutput(applications.data, template, applications.can_withdraw);
    } else {
        buildEmptyOutput();
    }
}

main();