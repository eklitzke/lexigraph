if (LX.dataset === undefined) {
    LX.dataset = {};
}

LX.dataset.show_delete = function (elt_id) {
    var img = document.getElementById(elt_id);
    img.style.visibility = "visible";
};

LX.dataset.hide_delete = function (elt_id) {
    var img = document.getElementById(elt_id);
    img.style.visibility = "hidden";
};

LX.dataset.show_add = function () {
    document.getElementById("add_img").style.visibility = "visible";
}

LX.dataset.hide_add = function () {
    document.getElementById("add_img").style.visibility = "hidden";
}

LX.dataset.add_series_xhr = function () {
    var n = document.getElementById("ds_name").value;
    var i = parseInt(document.getElementById("new_ival").value, 10);
    var m = parseInt(document.getElementById("new_max_age").value, 10);
    if (!i || !m) {
        return;
    }

    $.ajax({
        url: "/new/dataseries",
        type: "POST",
        dataType: "json",
        data: {dataset: n, interval: i, max_age: m},
        success: function (data) {
            if (data['code'] === 0) {
                /* Add the new series to the "existing series list" */
                var s = {id: data.id, interval: i, max_age: m};

                /* Ugh, this creates an extra div (there's already a div created by drawExistingSeries) */
                var d = document.createElement('div');
                d.id = "container_" + data.id;
                d.innerHTML = data['text']
                document.getElementById("existing_series").appendChild(d);

                /* Clear the input form. */
                document.getElementById("new_ival").value = "";
                document.getElementById("new_max_age").value = "";
            } else {
                alert("failed; code = " + data['code']);
            }
        }
    });
}

LX.dataset.draw_existing_series = function (series) {
    for (var i = 0; i < series.length; i++) {
        document.write(LX.soy.dataset.drawExistingSeries(series[i]));
    }
}

LX.dataset.remove_series_xhr = function (series_key) {
    $.ajax({
        url: "/delete/dataseries",
        type: "POST",
        data: {series_id: series_key},
        dataType: "json",
        success: function (data) {
            if (data.code) {
                alert("failed!");
            } else {
                // Find the containing div. This is either container_$key or
                // existing_$key (FIXME: this is stupid).
                var div;
                div = document.getElementById("container_" + series_key);
                if (div === null) {
                    div = document.getElementById("existing_" + series_key);
                }
                if (div === null) {
                    throw {"message": "failed to find the div"};
                }
                div.parentNode.removeChild(div);
            }
        }
    });
};

LX.dataset.redraw_xhr = function (data) {
    if (data['code'] === 0) {
        var tag, i;
        var existing = document.getElementById("existing_tags");
        existing.innerHTML = data['text'];

        /* Redraw the tag boxes */
        for (i = 0; i < data['tags'].length; i++) {
            tag = data['tags'][i]
            LX.canvas.box("tag_" + tag.name, tag);
        }
    } else {
        alert("failed; code = " + data['code']);
    }
};

LX.dataset.remove_tag_xhr = function (name) {
    $.ajax({
        url: "/ajax/remove/tag",
        type: "POST",
        dataType: "json",
        data: {"name": name, "key": datsetKey}, // hack: datasetKey will be available and global
        success: LX.dataset.redraw_xhr
    });
};

LX.dataset.add_tag_xhr = function (key) {
    var input = document.getElementById("new_tag");
    var name = input.value;
    $.ajax({
        url: "/ajax/add/tag",
        type: "POST",
        dataType: "json",
        data: {"name": name, "key": datasetKey}, // hack: datasetKey will be available and global
        success: function (data) {
            LX.dataset.redraw_xhr(data);
            if (data['code'] === 0) {
                /* Clear the input form. */
                input.value = "";
            }
        }
    });
};

LX.dataset.redraw_graph = function (width, name) {
    LX.updatePref("large_width", width);
    var elt = document.getElementById("graph_dataset_" + name);
    elt.style.width = width + "px";
    elt.style.height = parseInt(width / 2) + "px";
    LX.drawGraph({dataset_name: name});
};
