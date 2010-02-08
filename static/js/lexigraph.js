var LX = {};

/* This will be overridden by the servlet. */
LX.userPrefs = {};

LX.draw_graph = function (opts) {
    var dataset_name = opts.dataset_name || "zoinks";
    var element_id = opts.element_id;
    if (element_id === undefined) {
        element_id = "graph_dataset_" + dataset_name;
    }

    if (LX.tz_offset === undefined) {
        LX.tz_offset = (new Date()).getTimezoneOffset();
    }

    var draw_graph = function () {
        var lhs_time = new Date();
        var now = new Date();
        var div = document.getElementById(element_id);
        var csv_url = "/api/csv?dataset=" + dataset_name;
        if (LX.tz_offset) {
            csv_url += "&tz=" + LX.tz_offset;
        }

        /* dygraphs options are mixed in with other options */
        var graph_opts = {};
        var setopt = function (name, val) {
            if (opts[name] !== undefined) {
                graph_opts[name] = opts[name];
            } else {
                graph_opts[name] = val;
            }
        };
        var setuseropt = function (dg_name, lx_name, val) {
            if (LX.userPrefs[lx_name] !== undefined) {
                graph_opts[dg_name] = LX.userPrefs[lx_name];
            } else {
                graph_opts[dg_name] = val;
            }
        };

        setopt('includeZero', true);
        setopt('fillGraph', false);
        setuseropt('showRoller', 'show_rollbar', false);

        // Set the date window. Check opts.intervalSeconds first, and fallback to LX.userPrefs
        // if not opt is specified.
        if (opts.intervalSeconds !== undefined) {
            lhs_time.setSeconds(lhs_time.getSeconds() - opts.intervalSeconds);
        } else {
            lhs_time.setSeconds(lhs_time.getSeconds() - LX.userPrefs.default_timespan);
        }
        graph_opts.dateWindow = [lhs_time, now];

        new Dygraph(div, csv_url, graph_opts);
    };

    /* By default, defer the graph loading stuff until the page is fully
     * loaded.
     */
    if (opts.onload !== false) {

        LX.register_onload(draw_graph);
    } else {
        draw_graph();
    }
};

/* Create an onload registry function. This also sets up window.onload to use
 * this registry.
 */
LX.register_onload = (function () {
    var onload_handlers = [];

    window.onload = function () {
        var k;
        for (k in onload_handlers) {
            if (onload_handlers.hasOwnProperty(k)) {
                onload_handlers[k]();
            }
        }
    };

    return function (func) {
        onload_handlers.push(func);
    }
})();
