/**
 * Created by norbert on 8/07/2017.
 */

var State = function (socket) {

    var instance = this;
    var callBackEvent;
    this.type = "";

    {// init
        socket.emit('get_state', {});
    }

    socket.on('state', function(res){
        instance.type = res.state;
        console.log(res.state);
        if (callBackEvent) {
            callBackEvent(instance.type);
        }
    });

    this.on = function (callback) {
        callBackEvent = callback;
    }
};