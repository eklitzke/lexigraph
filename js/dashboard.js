LX.dashboard = {};

LX.graphQuery = function () {
    var input = document.getElementById("tags_query");

    $.getJSON("/ajax/graphs?tags=" + escape(input.value), function (data) {
        var graph_div = document.getElementById("query_results");
        graph_div.innerHTML = data.text;
        LX.drawGraphs(data.names);
    });
};

LX.dashboard.redraw_graphs = function (width) {
    var query_results = document.getElementById("query_results");
    var c, d, i, j;
    if (!query_results) {
        throw "failed to find 'query_results'"
    }
    LX.updatePref("small_width", width);
    for (i = 0; i < query_results.childNodes.length; i++) {
        c = query_results.childNodes[i];
        if (c.className == "inline_header") {
            for (j = 0; j < c.childNodes.length; j++) {
                d = c.childNodes[j];
                if (d.className == "lexigraph_chart") {
                    d.style.width = width + "px";
                    d.style.height = parseInt(width / 2) + "px";
                    var dsname = d.id.replace(/^graph_dataset_/, "");
                    // Force the graph to redraw
                    LX.drawGraph({dataset_name: dsname});
                }
            }
        }
    }
};

LX.dashboard.datasets_widget = (function () {
    $(function () {
        var cache = {};
        $("#composite_datasets").autocomplete({
            source: function (request, response) {
                if (cache.term == request.term && cache.content) {
                    response(cache.content);
                }
                if (new RegExp(cache.term).test(request.term) && cache.content && cache.content.length < 25) {
                    var matcher = new RegExp($.ui.autocomplete.escapeRegex(request.term), "i");
                    response($.grep(cache.content, function (value) {
                        return matcher.test(value.value);
                    }));
                }
                $.ajax({
                    url: "/search/dataset",
                    dataType: "json",
                    data: request,
                    success: function (data) {
                        cache.term = request.term;
                        cache.content = data;
                        response(data);
                    }
                });
            },
            minLength: 2
        });
    });
});
