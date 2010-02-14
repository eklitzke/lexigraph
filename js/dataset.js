goog.provide("LX.dataset");
goog.require("LX");
goog.require("LX.soy.dashboard");
goog.require("goog.dom");
goog.require("goog.net.XhrIo");

LX.dataset.write_graph = function (name, dims /* optional */) {
    if (!dims) {
        dims = LX.getGraphDimensions();
    }
    document.write(LX.soy.dashboard.graphWithTitle({name: name, dims: dims}));
};
goog.exportSymbol("LX.dataset.write_graph", LX.dataset.write_graph);

LX.dataset.show_delete = function (series_id) {
    var img = goog.dom.$("delete_img_" + series_id);
    img.style.visibility = "visible";
};
goog.exportSymbol("LX.dataset.show_delete", LX.dataset.show_delete);

LX.dataset.hide_delete = function (series_id) {
    var img = goog.dom.$("delete_img_" + series_id);
    img.style.visibility = "hidden";
};
goog.exportSymbol("LX.dataset.hide_delete", LX.dataset.hide_delete);

LX.dataset.show_add = function () {
    goog.dom.$("add_img").style.visibility = "visible";
}
goog.exportSymbol("LX.dataset.show_add", LX.dataset.show_add);

LX.dataset.hide_add = function () {
    goog.dom.$("add_img").style.visibility = "hidden";
}
goog.exportSymbol("LX.dataset.hide_add", LX.dataset.hide_add);

LX.dataset.add_series_xhr = function (e) {
    var n = goog.dom.$("ds_name").value;
    var i = parseInt(goog.dom.$("new_ival").value, 10);
    var m = parseInt(goog.dom.$("new_max_age").value, 10);
    if (!i || !m) {
        return;
    }
    var xhr = new goog.net.XhrIo();
    goog.events.listen(xhr, goog.net.EventType.COMPLETE, function (e) {
        var resp = this.getResponseJson();
        if (resp.success) {
            /* Clear the input form. */
            goog.dom.$("new_ival").value = "";
            goog.dom.$("new_max_age").value = "";

            /* Add the new series to the "existing series list" */
            alert("pretend like this just got ajaxed up north");
        } else {
            alert("got response: " + resp.success);
        }
    });
    xhr.send("/new/dataseries", "POST", "dataset=" + escape(n) + "&interval=" + escape(i) + "&max_age=" + escape(m));
}
goog.exportSymbol('LX.dashboard.add_series_xhr', LX.dashboard.add_series_xhr);

LX.dataset.remove_series_xhr = function (series_id) {
    var xhr = new goog.net.XhrIo();
    goog.events.listen(xhr, goog.net.EventType.COMPLETE, function (e) {
        var resp = this.getResponseJson();

    });
};
