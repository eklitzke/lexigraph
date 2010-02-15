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

LX.dataset.add_series_xhr = function () {
    var n = goog.dom.$("ds_name").value;
    var i = parseInt(goog.dom.$("new_ival").value, 10);
    var m = parseInt(goog.dom.$("new_max_age").value, 10);
    if (!i || !m) {
        return;
    }
    var xhr = new goog.net.XhrIo();
    goog.events.listen(xhr, goog.net.EventType.COMPLETE, function (e) {
        var resp = this.getResponseJson();
        if (resp['success']) {
            /* Add the new series to the "existing series list" */
            var s = {id: resp["id"], interval: i, max_age: m};

            /* Ugh, this creates an extra div (there's already a div created by drawExistingSeries) */
            var d = document.createElement('div');
            d.id = "container_" + resp["id"];
            d.innerHTML = LX.soy.dataset.drawExistingSeries(s);
            goog.dom.$("existing_series").appendChild(d);

            /* Clear the input form. */
            goog.dom.$("new_ival").value = "";
            goog.dom.$("new_max_age").value = "";
        } else {
            alert("got response: " + resp['success']);
        }
    });
    xhr.send("/new/dataseries", "POST", "dataset=" + escape(n) + "&interval=" + escape(i) + "&max_age=" + escape(m));
}
goog.exportSymbol('LX.dataset.add_series_xhr', LX.dataset.add_series_xhr);

LX.dataset.draw_existing_series = function (series) {
    var i;
    for (i = 0; i < series.length; i++) {
        var s = series[i];
        var t = {id: s['id'], interval: s['interval'], max_age: s['max_age']}; /* hack for soy */
        document.write(LX.soy.dataset.drawExistingSeries(t));
    }
}
goog.exportSymbol('LX.dataset.draw_existing_series', LX.dataset.draw_existing_series);

LX.dataset.remove_series_xhr = function (series_key) {
    var xhr = new goog.net.XhrIo();
    goog.events.listen(xhr, goog.net.EventType.COMPLETE, function (e) {
        var resp = this.getResponseJson();
        if (!resp['success']) {
            alert('failed');
        } else {
            /* Find the containing div. This is either container_$key or
             * existing_$key (FIXME: this is stupid).
             */
            var div;
            div = goog.dom.$("container_" + series_key);
            if (div === null) {
                div = goog.dom.$("existing_" + series_key);
            }
            if (div === null) {
                throw {"message": "failed to find the div"};
            }
            div.parentNode.removeChild(div);
        }
    });
    xhr.send("/delete/dataseries", "POST", "series_id=" + escape(series_key));
};
goog.exportSymbol('LX.dataset.remove_series_xhr', LX.dataset.remove_series_xhr);
