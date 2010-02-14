goog.provide("LX.dashboard");

goog.require("LX");
goog.require("LX.soy.dashboard");

LX.dashboard.draw_button = function () {
    var b1 = new goog.ui.Button('update graphs');
    b1.render(goog.dom.$('b1'));
    goog.events.listen(b1.getElement(), goog.events.EventType.CLICK, function (e) {
        LX.graphQuery('tags_query', 'query_results');
    });
}
goog.exportSymbol('LX.dashboard.draw_button', LX.dashboard.draw_button);

LX.dashboard.draw_initial_graphs = function (names, dims /* optional */) {
    if (!dims) {
        dims = LX.getGraphDimensions();
    }
    document.write(LX.soy.dashboard.graphsWithTitles({names: names, dims: dims}));
}
goog.exportSymbol('LX.dashboard.draw_initial_graphs', LX.dashboard.draw_initial_graphs);
