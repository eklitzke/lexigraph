goog.provide("lexigraph");

var LX = {};

/* This will be overridden by the servlet. */
LX.userPrefs = {};
//goog.exportProperty(LX, 'userPrefs', LX.userPrefs);

LX.drawGraph = function (opts) {
    var dataset_name = opts.dataset_name;
    if (dataset_name === undefined) {
        console.warn("failed to see dataset_name in call to LX.draw_graph");
        dataset_name = "zoinks";
    }

    var element_id = opts.element_id;
    if (element_id === undefined) {
        element_id = "graph_dataset_" + dataset_name;
    }

    var draw_graph = function () {
        console.debug('LX: drawing graph for "' + dataset_name + '"');
        var lhs_time = new Date();
        var now = new Date();
        var div = document.getElementById(element_id);
        var csv_url = "/api/csv?dataset=" + dataset_name;

        /* dygraphs options are mixed in with other options */
        var graph_opts = {};
        graph_opts.xValueParser = Dygraph.unixTimestampParser;
        graph_opts.xValueType = "date";
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
        setopt('colors', ['#5C7977', '#86997B', '#E8A03A', '#D24B14', '#2D292A']); //AIW pallet from colourlovers.com
        setopt('strokeWidth', 2);
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

    if (opts.onload === true) {
        google.setOnLoadCallback(draw_graph);
    } else {
        draw_graph();
    }
};

LX.graphQuery = function (input_id, div_id) {
    var input, graph_div, tag_list = [], tag, i;
    input = document.getElementById(input_id);

    goog.net.XhrIo.send("/graph/query?q=" + escape(input.value || ""), function (e) {
        data = this.getResponseJson();
        graph_div = document.getElementById(div_id);
        var elt_list = [];

        var subgraph_width = parseInt(LX.userPrefs.large_width, 10) + "px";
        var subgraph_height = parseInt(LX.userPrefs.large_width / 1.618, 10) + "px";

        // create the new elements, but don't add them to the DOM yet; instead,
        // push them onto elt_list
        for (i = 0; i < data.datasets.length; i++) {
            var dataset_name = data.datasets[i];

            var h_div = document.createElement("div");
            h_div.className = "inline_header";

            var h_tag = document.createElement("h2");
            h_tag.appendChild(document.createTextNode(dataset_name));
            h_div.appendChild(h_tag);

            var h_link = document.createElement("a");
            h_link.setAttribute("href", "/edit/dataset?name=" + dataset_name);
            h_link.className = "mini_link";
            h_link.appendChild(document.createTextNode("edit"));
            h_div.appendChild(h_link);

            elt_list.push(h_div);


            var subgraph_div = document.createElement("div");
            subgraph_div.id = "graph_dataset_" + dataset_name;
            subgraph_div.className = "lexigraph_chart";
            subgraph_div.style.width = subgraph_width;
            subgraph_div.style.height = subgraph_height;
            elt_list.push(subgraph_div);
        }

        // ok, now elt_list has all of the elements we want. delete all of the
        // old children of graph_div, and add all of the elements in
        // elt_list.
        while (graph_div.childNodes.length >= 1) {
            graph_div.removeChild(graph_div.firstChild);
        }
        for (i = 0; i < elt_list.length; i++) {
            graph_div.appendChild(elt_list[i]);
        }

        // last thing to do is to ask dygraphs to render everything
        for (i = 0; i < data.datasets.length; i++) {
            LX.drawGraph({onload: false, dataset_name: data.datasets[i]});
        }
    });
};
