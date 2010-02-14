goog.provide("LX.ui");
goog.require("goog.dom");

LX.ui.draw_button = function (element_id, text, click_cb) {
    var button = new goog.ui.Button(text);
    button.render(goog.dom.$(element_id));
    if (click_cb) {
        goog.events.listen(button.getElement(), goog.events.EventType.CLICK, click_cb);
    }
}
goog.exportSymbol('LX.ui.draw_button', LX.ui.draw_button);
