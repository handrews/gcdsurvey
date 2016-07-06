// Load the Visualization API and the charting packages.
google.charts.load('current', {packages: ['corechart',
                                          'sankey',
                                          'table',
                                          'controls']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    // This should be the only reference to the global data variable.
    // See data.json for its definition.
    var rawData = GCDSurveyData;

    var chartConfig;
    var pie;
    var stack;
    Object.keys(rawData).forEach(function(chartName) {
        chartConfig = rawData[chartName];
        if (rawData[chartName].type === 'pie') {
            pie = new google.visualization.PieChart(
                document.getElementById(chartConfig.target));
            pie.draw(
                new google.visualization.DataTable(chartConfig.data),
                {
                    title: chartName,
                    pieSliceText: 'value'
                });

        } else if (rawData[chartName].type === 'stack') {
            stack = new google.visualization.ColumnChart(
                document.getElementById(chartConfig.target));
            stack.draw(
                new google.visualization.DataTable(chartConfig.data),
                {
                    title: chartName,
                    isStacked: 'percent',
                    legend: {position: 'bottom'}
                });
        }
    });
    // Set up the unmodified data as a DataTable.
    var data = new google.visualization.DataTable(GCDRawData);
                                
    // Whole data table
    var table = new google.visualization.Table(
        document.getElementById('raw_table_div'));
    table.draw(data);
}
