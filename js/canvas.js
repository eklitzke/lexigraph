LX.canvas = {}

LX.canvas.box = function (elt_id, opts) {
    var elt = document.getElementById(elt_id);
    if (elt === null) {
        throw "no such elt " + elt_id;
    }
    var ctx = elt.getContext("2d");
    if (ctx === null) {
        throw "no context 2d";
    }

    if (opts.alpha) {
        ctx.fillStyle = "rgba(" + opts.red + "," + opts.green + "," + opts.blue + "," + opts.alpha + ")";
    } else {
        ctx.fillStyle = "rgb(" + opts.red + "," + opts.green + "," + opts.blue + ")";
    }
    ctx.fillRect(0, 0, elt.width, elt.height);

    if (opts.outline) {
        ctx.fillStyle = "rgb(0,0,0)";
    }
    ctx.strokeRect(0, 0, elt.width, elt.height);
}
