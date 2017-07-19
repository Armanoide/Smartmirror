/**
 * Created by norbert on 9/07/2017.
 */

var User = function (socket) {

    var instance = this;
    this.info = null;

    var callbackEvent = null;

    {// init
        socket.emit('get_me', {});
    }

    socket.on('user', function (data) {

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