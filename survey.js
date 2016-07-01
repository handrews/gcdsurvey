// Load the Visualization API and the charting packages.
google.charts.load('current', {'packages':['corechart',
                                           'sankey',
                                           'table',
                                           'controls']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    // This should be the only reference to the global data variable.
    // See data.json for its definition.
    var rawData = GCDSurveyData;
    // rawData.rows.sort(getSortByBasicReason(rawData));


    var pieChartConfig;
    var pie;
    var stackChartConfig;
    var stack;
    Object.keys(rawData).forEach(function(chartName) {
        if (rawData[chartName].type == 'pie') {
            pieChartConfig = rawData[chartName];
            pie = new google.visualization.PieChart(
                document.getElementById(pieChartConfig.target));
            pie.draw(new google.visualization.DataTable(pieChartConfig.data),
                     {title: chartName, pieSliceText: 'value'});
        } else if (rawData[chartName].type == 'stack') {
            stackChartConfig = rawData[chartName];
            stack = new google.visualization.ColumnChart(
                document.getElementById(stackChartConfig.target));
            stack.draw(new google.visualization.DataTable(stackChartConfig.data),
                       {title: chartName,
                        isStacked: 'percent',
                        legend: {position: 'bottom'}});
        }
    });
/*
    var euroTitle = 'Europe by Country';
    var euroConfig = rawData[euroTitle];
    var euroPie = new google.visualization.PieChart(
        document.getElementById(euroConfig.target));
    euroPie.draw(new google.visualization.DataTable(euroConfig.data),
                 {title: euroTitle, pieHole: 0.6});
/*
    var prefBySocialTitle ='Preference by Socialness'; 
    var prefBySocialConfig = rawData[prefBySocialTitle];
    var prefBySocialChart = new google.visualization.ColumnChart(
        document.getElementById(prefBySocialConfig.target));
    prefBySocialChart.draw(
        new google.visualization.DataTable(prefBySocialConfig.data),
        {title: prefBySocialTitle, 'isStacked': 'percent'});

/*
    comparisonStackChart('why_columns', data, rawData, 'basic_why', 'basic_social');
    rawData.rows.sort(getSortByRegion(rawData));
    data = new google.visualization.DataTable(rawData);
    comparisonStackChart('preference_columns', data, rawData, 'gender', 'basic_why');

    // Regions
    var regionIndex = getColumnIndex(rawData, 'region');
    var regionPie = new google.visualization.PieChart(
        document.getElementById('region_div'));
    regionPie.draw(getCountView(data, regionIndex, genericLabels, getSortByNumber));

    filteredCountChart(data, rawData, 'europe_div', 'region', 'europe',
                       'country', undefined, countryLabels);
    filteredCountChart(data, rawData, 'latin_america_div',
                      'region', 'latin america', 'country',
                      undefined, countryLabels);
    filteredCountChart(data, rawData, 'pacific_anglophone_div',
                       'region', 'pacific anglophone', 'country',
                       undefined, countryLabels);

    // Social
    var basicSocialPie = new google.visualization.PieChart(
        document.getElementById('basic_social_div'));
    basicSocialPie.draw(getCountView(data,
                                  getColumnIndex(rawData, 'basic_social')));

    var genderChart = new google.visualization.PieChart(
        document.getElementById('gender'));
    genderChart.draw(getCountView(data,
                                  getColumnIndex(rawData, 'gender')));
    filteredCountChart(data, rawData, 'research_gender', 'basic_why',
                       'research', 'gender');
 */ 
    // Set up the unmodified data as a DataTable.
    var data = new google.visualization.DataTable(GCDRawData);
                                
    // Whole data table
    var table = new google.visualization.Table(
        document.getElementById('raw_table_div'));
    table.draw(data);
};

/*
function unsortedDistinctColumnValues(data, rawData, colName) {
    var colIndex = getColumnIndex
    values = [];
    for (var i = 0; i < data.getNumberOfRows(); ++i) {
        if (data.get
};
*/

function getSortByBasicReason(rawData) {
    var i = getColumnIndex(rawData, 'basic_why');
    var sortMap = {
        'personal interest': 1,
        research: 2,
        interactive: 3
    };
    return getSortBySortMap(i, sortMap);
};

function getSortByRegion(rawData) {
    var i = getColumnIndex(rawData, 'region');
    var sortMap = {
        'united states': 1,
        'europe': 2,
        'united kingdom': 3,
        'canada': 4,
        'latin america': 5,
        'pacific anglophone': 6,
        'north africa': 7,
        'unspecified': 8
    };
    return getSortBySortMap(i, sortMap);
};

function getSortBySortMap(i, sortMap) {
    return function(a, b) {
        var aVal = sortMap[a.c[i].v]
        var bVal = sortMap[b.c[i].v]

        return numberHelper(aVal, bVal);
    };
};

function getSortByNumber(i, sortMap) {
    return function(a, b) {
        return numberHelper(a.c[i], b.c[i]);
    }
};

function numberHelper(a, b) {
    if (a < b) {
        return -1;
    } else if (a > b) {
        return 1;
    }
    return 0;
};

/*
    return function(a, b) {
        if (a.c[i].v == b.c[i].v) {
            return 0;
        }
        if (a.c[i].v == 'personal interest' || b.c[i].v == 'interactive') {
            return -1;
        }
        if (a.c[i].v == 'interactive' || b.c[i].v == 'personal interest') {
            return 1;
        }
        // Only three options, should not be possible to get here.
        throw "Unknown value for basic reason!"
    };
*/
