const get_applications_data = new Promise((resolve, reject) => {
    $.ajax({
        dataType: "json",
        error: (jqXHR, textStatus, errorThrown) => {
            debugger;
            reject(errorThrown);
        },
        success: (data, textStatus, jqXHR) => {
            resolve(data)
        },
        method: "GET",
    });
});

const get_template = new Promise((resolve, reject) => {
    try {
        const template_url = `${STATIC_URL}web/FE_templates/applications/applications_to_my_courses_course_card.njk`;
        $.ajax({
            method: "GET",
            url: template_url,
            dataType: "html",
            success: (data, textStatus, jqXHR) => {
                // nunjucks global config
                var env = nunjucks.configure(STATIC_URL, {
                    autoescape: true,
                    trimBlocks: true,
                    lstripBlocks: true,
                });
                var template = nunjucks.compile(data, env);
                resolve(template);
            },
            error: (jqXHR, textStatus, errorThrown) => {
                reject(errorThrown);
            },
        });
    } catch (err) {
        reject(err);
    }
});


const build_output = (data, template) => {
    // convenience rename
    const all_applications = data.applications;

    // DOM manipulation
    const root_node = document.getElementById('applications');

    const uniqueYears = Array.from(new Set(all_applications.map(item => item.year)));
    for (const year of uniqueYears) {

        // DOM manipulation
        const year_node = document.createElement("h4");
        const year_text = document.createTextNode(year);
        year_node.appendChild(year_text);
        year_node.classList.add("alert");
        year_node.classList.add("alert-info");
        root_node.appendChild(year_node);

        // get all the courses for the given year
        const this_year_applications = all_applications.filter(item => item.year === year);

        // get all the terms present in this list of courses
        const uniqueTerms = Array.from(new Set(this_year_applications.map(item => item.term)));

        for (const term of uniqueTerms) {
            // DOM manipulation
            var term_node = document.createElement("h5");
            var term_text = document.createTextNode(term);
            term_node.appendChild(term_text);
            term_node.classList.add("alert");
            term_node.classList.add("alert-primary");
            year_node.insertAdjacentElement("afterend", term_node)

            const this_term_applications = this_year_applications.filter(item => item.term === term);

            const uniqueCourses = Array.from(new Set(this_term_applications.map(item => item.subject)));

            for (const course of uniqueCourses) {
                const this_course_applications = this_term_applications.filter(item => item.subject === course);

                const accepted_applications = this_course_applications.filter(item => item.status === "Hired");
                const has_accepted_applications = accepted_applications.length > 0 ? true : false
                const rejected_applications = this_course_applications.filter(item => item.status === "Rejected");
                const has_rejected_applications = rejected_applications.length > 0 ? true : false
                const pending_applications = this_course_applications.filter(item => item.status === "Pending");
                const has_pending_applications = pending_applications.length > 0 ? true : false
                const withdrawn_applications = this_course_applications.filter(item => item.status === "Withdrawn");
                const has_withdrawn_applications = withdrawn_applications.length > 0 ? true : false

                var result = template.render({
                    applications: this_course_applications,
                    has_accepted_applications: has_accepted_applications,
                    accepted_applications: accepted_applications,
                    has_rejected_applications: has_rejected_applications,
                    rejected_applications: rejected_applications,
                    has_pending_applications: has_pending_applications,
                    pending_applications: pending_applications,
                    has_withdrawn_applications: has_withdrawn_applications,
                    withdrawn_applications: withdrawn_applications,
                });
                term_node.insertAdjacentHTML("afterend", result);
            }
        }
    }
}

$(document).ready(() => {
    Promise.all([get_applications_data, get_template]).then((values) => {
        build_output(values[0], values[1]);
    });
});