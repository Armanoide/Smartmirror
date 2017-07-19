/**
 * Created by norbert on 9/07/2017.
 */

var Weather = function (socket) {

    var instance = this;
    this.info = null;

    var callbackEvent = null;

    socket.on('weather', function (data) {

        if ("string" == typeof (data)){
            instance.info = JSON.parse(data);
        } else {
            instance.info = data;
        }

        if (callbackEvent) {
            callbackEvent(instance.info);
        }
    });

    this.on = function(callback) {
        callbackEvent = callback;
    };
};