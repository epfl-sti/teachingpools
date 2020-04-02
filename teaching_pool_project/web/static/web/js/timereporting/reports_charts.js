function get_chart_data() {
    return new Promise(function(resolve, reject) {
        let data_chart_1 = [];
        let labels_chart_1 = [];
        $.ajax({
            url: chart_1_endpoint,
            success: function(data, textStatus, jqXHR) {
                for (idx in data) {
                    data_chart_1.push(data[idx]['hours']);
                    labels_chart_1.push(data[idx]['activity_type']);
                }
                resolve({ 'data': data_chart_1, 'labels': labels_chart_1 });
            },
            error: function(jqXHR, textStatus, errorThrown) {
                reject(Error(textStatus));
            }
        });
    });
}

function build_chart_1(server_data) {
    var ctx = document.getElementById('chart_1').getContext('2d');
    Chart.defaults.global.defaultFontFamily = 'Roboto';
    var chart_1 = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: server_data['labels'],
            datasets: [{
                label: 'Hours',
                data: server_data['data'],
                yAxisID: 'y-axis',
            }],
        },
        options: {
            title: {
                display: true,
                text: "Average number of hours per category",
                fontSize: 14,
                fontStyle: 'bold',
            },
            legend: {
                display: false,
            },
            scales: {
                yAxes: [{
                    id: 'y-axis',
                    scaleLabel: {
                        display: true,
                        labelString: 'Hours',
                    },
                }]

            },
            plugins: {
                colorschemes: {
                    scheme: 'tableau.Tableau20',
                }
            },
        },
    });
}

$(document).ready(function() {
    get_chart_data()
        .then(function(response) {
            build_chart_1(response);
        })
        .catch(function(error) {
            console.log(error);
        });
});