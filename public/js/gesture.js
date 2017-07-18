/**
 * Created by norbert on 8/07/2017.
 */


var Gesture = function (socket) {

    var instance = this;
    var callbackEvent = null;
    instance.count_circle_convex = "";
    instance.position_hand_vertical = "";
    instance.position_hand_horizontal = "";


    {// init
        socket.on('count_circle_convex', function(res){
            if (res.count_circle_convex != instance.count_circle_convex){
                $("#debug_count_circle_convex").text("count_circle_convex: " + res.count_circle_convex);
            }
            instance.count_circle_convex = res.count_circle_convex;
            if (callbackEvent) {
                callbackEvent("count_circle_convex", instance.count_circle_convex);
            }
        });


        socket.on('position_hand_vertical', function(res){
            if (res.position_hand_vertical != instance.position_hand_vertical){
                $("#debug_position_hand_vertical").text(res.position_hand_vertical);
            }
            instance.position_hand_vertical = res.position_hand_vertical;
            if (callbackEvent) {
                callbackEvent("position_hand_vertical", instance.position_hand_vertical);
            }

        });


        socket.on('position_hand_horizontal', function(res){
            if (res.position_hand_horizontal != instance.position_hand_horizontal){
                $("#debug_position_hand_horizontal").text(res.position_hand_horizontal);
            }

            instance.position_hand_horizontal = res.position_hand_horizontal;
            if (callbackEvent) {
                callbackEvent("position_hand_horizontal", instance.position_hand_horizontal);
            }


        });

        this.on = function (callback) {
            callbackEvent = callback;
        };


    }

};