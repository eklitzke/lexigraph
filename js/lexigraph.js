goog.provide("LX");
goog.require('goog.net.XhrIo');

LX.userPrefs = {}
goog.exportProperty(LX, 'userPrefs', LX.userPrefs);

LX.getPref = function (name, value) {
    if (name in LX.userPrefs) {
        return LX.userPrefs[name];
    } else {
        return value;
    }
}

LX.updatePrefs = function (map) {
    var k;
    for (k in map) {
        if (map.hasOwnProperty(k)) {
            LX.userPrefs[k] = map[k];
        }
    }
};
goog.exportSymbol('LX.updatePrefs', LX.updatePrefs);

LX.drawGraph = function (opts) {
    var dataset_name = opts.dataset_name;
    if (dataset_name === undefined) {
        throw {name: "undefined dataset", args: opts};
    }

    var element_id = opts.element_id;
    if (element_id === undefined) {
        element_id = "graph_dataset_" + dataset_name;
    }

    var draw_graph = function () {
        var lhs_time = new Date();
        var now = new Date();
        var div = goog.dom.$(element_id);
        var csv_url = "/api/csv?dataset=" + dataset_name;

        /* dygraphs options are mixed in with other options */
        var graph_opts = {};
        graph_opts['xValueParser'] = window['Dygraph']['unixTimestampParser'];
        graph_opts['xValueType'] = "date";
        var setopt = function (name, val) {
            if (name in opts) {
                graph_opts[name] = opts[name];
            } else {
                graph_opts[name] = val;
            }
        }
        var setuseropt = function (dg_name, lx_name, val) {
            if (LX.userPrefs[lx_name] !== undefined) {
                graph_opts[dg_name] = LX.userPrefs[lx_name];
            } else {
                graph_opts[dg_name] = val;
            }
        };

        setopt('includeZero', true);
        setopt('fillGraph', false);
        setopt('colors', ['#5C7977', '#86997B', '#E8A03A', '#D24B14', '#2D292A']); //AIW pallet from colourlovers.com
        setopt('strokeWidth', 2);
        setuseropt('showRoller', 'show_rollbar', false);

        // Set the date window. Check opts.intervalSeconds first, and fallback to LX.userPrefs
        // if not opt is specified.
        if (opts.intervalSeconds !== undefined) {
            lhs_time.setSeconds(lhs_time.getSeconds() - opts.intervalSeconds);
        } else {
            lhs_time.setSeconds(lhs_time.getSeconds() - LX.getPref('default_timespan'));
        }
        graph_opts['dateWindow'] = [lhs_time, now];

        new window['Dygraph'](div, csv_url, graph_opts);
    };

    draw_graph();
};
goog.exportSymbol('LX.drawGraph', LX.drawGraph);

LX.getGraphDimensions = function () {
    if (LX.userPrefs) {
        return {width: LX.userPrefs['large_width'],
                height: parseInt(LX.userPrefs['large_width'] / 1.618, 10)};
    }
    return null;
}
goog.exportSymbol('LX.getGraphDimensions', LX.getGraphDimensions);

LX.drawGraphs = function (datasets, onLoad) {
    if (onLoad === undefined) {
        onLoad = false;
    }
    for (var i = 0; i < datasets.length; i++) {
        LX.drawGraph({onload: onLoad, dataset_name: datasets[i]});
    }
};
goog.exportSymbol('LX.drawGraphs', LX.drawGraphs);

LX.graphQuery = function (input_id, div_id) {
    var input, graph_div, tag_list = [], tag, i;
    input = document.getElementById(input_id);

    goog.net.XhrIo.send("/graph/query?q=" + escape(input.value || ""), function (e) {
        data = this.getResponseJson();
        graph_div = goog.dom.$(div_id);
        graph_div.innerHTML = LX.soy.dashboard.graphsWithTitles({names: data.datasets, dims: LX.getGraphDimensions()});
        LX.drawGraphs(data.datasets);
    });
};
goog.exportSymbol('LX.graphQuery', LX.graphQuery);
