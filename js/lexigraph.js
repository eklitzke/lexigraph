var LX;
if (LX === undefined) {
    LX = {};
}

LX.userPrefs = {}

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

LX.drawGraph = function (opts) {
    var datasets = opts.datasets;
    if (datasets === undefined) {
        throw {name: "undefined datasets", args: opts};
    }

    var element_id = opts.element_id;
    if (element_id === undefined) {
        if (opts.dataset_id === undefined) {
            throw "must have an element_id or dataset_id defined";
        } else {
            element_id = "graph_dataset_" + opts.dataset_id;
        }
    }

    var draw_graph = function () {
        var lhs_time = new Date();
        var now = new Date();
        var div = document.getElementById(element_id);
        if (!div) {
            throw {"name": "no such element", args: element_id};
        }
        if (!div.style.width || !div.style.height) {
            var dims = LX.getGraphDimensions();
            div.style.width = dims.width + "px";
            div.style.height = dims.height + "px";
        }
        var csv_url = "/api/csv?";
        var need_amp = false;
        for (var i = 0; i < datasets.length; i++) {
            if (need_amp) {
                csv_url += "&";
            } else {
                need_amp = true;
            }
            csv_url += "dataset=" + datasets[i];
        }

        /* dygraphs options are mixed in with other options */
        var graph_opts = {};
        graph_opts.xValueParser = Dygraph.unixTimestampParser;
        graph_opts.xValueType = "date";
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
        // setopt('colors', ['#5C7977', '#86997B', '#E8A03A', '#D24B14', '#2D292A']); //AIW pallet from colourlovers.com
        //setopt('colors', ['#3F4C5F', '#A81213', '#467040', '#E7FE4C', '#D75A7C']); // http://kuler.adobe.com/#themeID/802345
        //setopt('colors', ['#471045', '#FF7000', '#BD2056', '#648C02', '#FFD300']);
        setopt('colors', ['#3f4c5f', '#66b132', '#0248ff', '#fd5202']);
        setopt('strokeWidth', 2);
        setuseropt('showRoller', 'show_rollbar', false);

        // Set the date window. Check opts.intervalSeconds first, and fallback to LX.userPrefs
        // if not opt is specified.
        if (opts.intervalSeconds !== undefined) {
            lhs_time.setSeconds(lhs_time.getSeconds() - opts.intervalSeconds);
        } else {
            lhs_time.setSeconds(lhs_time.getSeconds() - LX.getPref('default_timespan'));
        }
        graph_opts.dateWindow = [lhs_time, now];
        new Dygraph(div, csv_url, graph_opts);
    };

    draw_graph();
};

LX.getGraphDimensions = function () {
    if (LX.userPrefs) {
        return {width: LX.userPrefs['small_width'],
                height: parseInt(LX.userPrefs['small_width'], 10) / 2};
    }
    return null;
}

LX.drawGraphs = function (datasets, onLoad) {
    if (onLoad === undefined) {
        onLoad = false;
    }
    for (var i = 0; i < datasets.length; i++) {
        LX.drawGraph({onload: onLoad, dataset_name: datasets[i]});
    }
};

LX.updatePref = function (name, value) {
    LX.userPrefs[name] = value;
    $.ajax({
        url: "/ajax/prefs",
        type: "POST",
        dataType: "json",
        data: {"name": name, "value": value},
        success: function (data) {
            if (data['status'] != 0) {
                alert(data);
            }
        }
    });

};
