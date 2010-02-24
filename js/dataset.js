if (LX.dataset === undefined) {
    LX.dataset = {};
}

LX.dataset.show_delete = function (series_id) {
    var img = document.getElementById("delete_img_" + series_id);
    img.style.visibility = "visible";
};

LX.dataset.hide_delete = function (series_id) {
    var img = document.getElementById("delete_img_" + series_id);
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
            if (data['success']) {
                /* Add the new series to the "existing series list" */
                var s = {id: data.id, interval: i, max_age: m};

                /* Ugh, this creates an extra div (there's already a div created by drawExistingSeries) */
                var d = document.createElement('div');
                d.id = "container_" + data.id;
                d.innerHTML = LX.soy.dataset.drawExistingSeries(s); // XXX: FIXME
                document.getElementById("existing_series").appendChild(d);

                /* Clear the input form. */
                document.getElementById("new_ival").value = "";
                document.getElementById("new_max_age").value = "";
            } else {
                alert("failed");
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
            if (!resp.success) {
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
