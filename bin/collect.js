var sys = require("sys");
var http = require("http");

/* Get a value from the environment, falling back to a default */
function getEnv(name, value) {
    return (name in process.env ? process.env[name] : value);
}

var SHELL = getEnv("SHELL", "/bin/bash");
var ADD_POINT = getEnv("ADD_POINT", "./src/add_point");

var LX_HOST = getEnv("LX_HOST", "lexigraph.appspot.com");
var LX_PORT = parseInt(getEnv("LX_PORT", 80));

/**
 * Escape a string in the format specified by the
 * application/x-www-form-urlencoded MIME type.
 * @param str the string to form escape
 */
function formEscape(str) {
    return escape(str.replace(/ /g, '+'));
}

/**
 * Encode a map for a POST request.
 * @param map the map to encode
 */
function formEncode(map) {
    var k;
    var msg = "";

    for (k in map) {
        if (map.hasOwnProperty(k)) {
            msg += '&' + formEscape(k) + '=' + formEscape(map[k]);
        }
    }
    return msg.slice(1);
}

this.upload = upload = function (name, key, val) {
    var client = http.createClient(LX_PORT, LX_HOST);
    var form = formEncode({dataset: name, key: key, value: val});
    var req = client.request("POST", "/api/new/datapoint",
                             {"Content-Type": "application/x-www-form-urlencoded; charset=us-ascii",
                              "Host": LX_HOST,
                              "Content-Length": form.length,
                              "Connection": "close",
                              "User-Agent": "lexigraph-collector/0.1"});
    req.addListener("response", function (response) {
        response.addListener("complete", function () {
            if (response.statusCode != 200) {
                sys.debug("Got error response: " + response.statusCode);
                sys.debug("Headers: " + sys.inspect(response.headers));
            }
        });
    });
    req.write(form, encoding="ascii");
    req.close();
};

var COMMANDS = [
    {"cmd": "cut -f1 -d' ' /proc/loadavg", "interval": 30, "key": "bc98d09c5915ef1c19e1e21bfd51a111", "name": "B1S97Fy1PH4Q6qaeDgZDJA"},
    {"cmd": "cut -f2 -d' ' /proc/loadavg", "interval": 30, "key": "bc98d09c5915ef1c19e1e21bfd51a111", "name": "e9qhIa3r4C4wUMwoMgYMLA"},
    {"cmd": "cut -f3 -d' ' /proc/loadavg", "interval": 30, "key": "bc98d09c5915ef1c19e1e21bfd51a111", "name": "CA1SdpOJV5qzRTdoggQpGg"}
];

function commandLoop(params) {
    var f = function () {
        var start = (new Date()).valueOf();
        var out = "", err = "";
        process.createChildProcess(SHELL, ["-c", params.cmd]).
            addListener("output", function (data) {
                if (data !== null) {
                    out += data;
                }
            }).
            addListener("error", function (data) {
                if (data !== null) {
                    err += data;
                }
            }).
            addListener("exit", function (code) {
                if (code == 0) {
                    upload(params.name, params.key, out.replace(/^\s+|\s+$/g,""));
                } else {
                    sys.debug("WTF: " + code);
                }
            });
        var now = (new Date()).valueOf();
        setTimeout(f, params.interval * 1000 - (now - start));
    }
    f();
}

/* Spawn loops for each command */
var i;
for (i = 0; i < COMMANDS.length; i++) {
    commandLoop(COMMANDS[i]);
};
