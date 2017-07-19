/**
 * Created by norbert on 9/07/2017.
 */

var clock;
var animationMenuEnd = true;
var socket;
var gesture;
var state;
var menu;
var weather;
var user;
var news;
// like weather ...
var appRunning = null;
var isAvaiableForGesture = true;
var slyManager = null;

var slyOption = {
    horizontal: 2,
    itemNav: 'centered',
    smart: 1,
    activateOn: 'click',
    mouseDragging: 1,
    touchDragging: 1,
    releaseSwing: 1,
    startAt: 4,
    scrollBy: 1,
    speed: 300,
    elasticBounds: 1,
    easing: 'easeOutExpo',
    dragHandle: 1,
    dynamicHandle: 1,
    clickBar: 1,
};

display_status_off();
$(document).ready(function() {
    clock = $('.clock').FlipClock({
        clockFace: 'TwentyFourHourClock'
    });

    //display_status_in_use();
    socket = io('http://localhost:3000', {transport:['websocket']});
    menu = new MenuManager();
    // if server connected and accept
    socket.on('connect', function(){

        gesture = new Gesture(socket);
        state = new State(socket);
        weather = new Weather(socket);
        user  = new User(socket);
        news = new News(socket);
        bind()

    });
    socket.on('disconnect', function(){ display_no_connection(); });
    // if server is disconnected displa it

    socket.on('hsv_img', function (data) {
        var b64 = "data:image/jpeg;base64," + data.hsv_img;
        $('#img-debug').attr('src', b64);
    });

    function bind() {

        gesture.on(function (type, value) {

            if (!appRunning && gesture.position_hand_vertical
                && gesture.position_hand_vertical === "UP"
                && animationMenuEnd === true) {
                animationMenuEnd = false;
                $("#cn-button").click();
                setTimeout(function () {
                    animationMenuEnd = true;
                }, 2000);
            }


            if (appRunning && gesture.position_hand_vertical
                && gesture.position_hand_vertical === "UP") {
                display_status_off();
                display_status_in_use();
                appRunning = null;
            }

            if (state.type == "IN_USE" && menu.isOpen === false && isAvaiableForGesture === true
                && appRunning == "news") {

                isAvaiableForGesture = false;

                setTimeout(function(){
                    isAvaiableForGesture = true;
                }, 1000);

                if (gesture.position_hand_horizontal === "LEFT") {
                    slyManager.prev()
                }
                if (gesture.position_hand_horizontal === "RIGHT") {
                    slyManager.next();
                }


            }

            if (state.type === "IN_USE" && menu.isOpen === true && isAvaiableForGesture === true) {

                isAvaiableForGesture = false;

                setTimeout(function(){
                    isAvaiableForGesture = true;
                }, 1000);


                var lastPosition =   parseInt($("#cn-wrapper").attr("position"));

                if (gesture.count_circle_convex >= 3) {
                    console.log("selection nb " + lastPosition);
                    $("#cn-wrapper li:nth-child("+lastPosition+") a").click();
                }

                if (gesture.count_circle_convex > 2) {
                    return
                }

                if (lastPosition === -1) {
                    lastPosition = 1;
                }
                console.log("lastPosition");
                console.log(lastPosition);

                if (gesture.position_hand_horizontal === "LEFT") {
                    lastPosition--;
                }
                if (gesture.position_hand_horizontal === "RIGHT") {
                    lastPosition++;
                }
                if (lastPosition <= 0) {
                    lastPosition = 1;
                }
                if (lastPosition > $("#cn-wrapper li").length) {
                    lastPosition = $("#cn-wrapper li").length
                }
                console.log("after eval lastPosition");
                console.log(lastPosition);

                $("#cn-wrapper li").each(function(){
                    $(this).removeClass('hover');
                });

                $("#cn-wrapper li:nth-child("+lastPosition+")").addClass('hover');
                $("#cn-wrapper").attr('position', lastPosition);

            }
        });


        weather.on(function (data) {

            if (data) {
                $('#weather-temp').text(data.temperature || "-");
                $('#weather-phrase').text(data.phrase || "-");
            }

        });

        user.on(function (user) {

            $('#welcome-message').text("Welcome " + user.first_name + " " + user.last_name + " !");
            $('#my-info-name').text(user.first_name + " " + user.last_name);
            $('#my-location').text(user.city || "-");
            $('#my-location').text(user.latitude + "," + user.longitude);

        });

        news.on(function (data) {
            var list = $('#news-frame ul');
            list.empty();
            for (var i = 0; i < data.length; i++) {
                var e = data[i];
                var li = '' +
                    '<li>'+
                    '   <div class="news-photo">'+
                    '       <img src="'+ e.urlToImage +'">'+
                    '   </div>'+
                    '   <div class="news-text">'+
                    '       <h1 class="news-title">'+ e.title +'</h1>'+
                    '       <p class="news-description">'+ e.description +'</p>'+
                    '       <p class="news-time">'+ moment(new Date(e.publishedAt)).fromNow() +'</p>'+
                    '   </div>'+
                    '</li>';
                list.append(li);
            }
            slyManager = new Sly($('#news-frame'), slyOption);
            slyManager.init().destroy().init();

        });

        state.on(function (type) {
            if (type === "OFF") {
                display_status_off();
            }
            if (type === "STANDBY"){
                display_status_standby();
            }
            if (type === "RECORDING"){
                display_status_recording();
            }
            if (type === "DETECTION") {
                display_status_recording();
            }
            if (type === "IN_USE") {
                display_status_in_use();
            }

        });
    }
});



function display_status_off() {
    $('#news').hide();
    $('#hand-red').hide();
    $('.circle1').hide();
    $('.circle').hide();
    $('#welcome-message').hide();
    $('#unlock-message').hide();
    $('#no-connection').hide();
    $('#cn-button').hide();
    $('#weather').hide();
    $('#my_info').hide();
}

function display_status_standby() {
    display_status_off();
    $('#hand-red').show();
    $('#welcome-message').show();
    $('#unlock-message').show();
    $('#no-connection').hide();
}

function display_status_recording() {
    display_status_off();
    $('.circle1').show();
    $('.circle').show();
    $('#welcome-message').show();
}

function display_status_in_use() {
    display_status_off();
    $('#cn-button').show();
}

function display_no_connection() {
    $('#no-connection').show();
    $('#hand-red').hide();
    $('.circle1').hide();
    $('.circle').hide();
    $('#welcome-message').hide();
    $('#unlock-message').hide();
    $('#cn-button').hide();
}

function display_weather() {
    appRunning = "weather";
    display_status_off();
    menu.close();
    $("#weather").show();
    socket.emit('get_weather', {});
}

function display_my_info() {
    appRunning = "my_info";
    display_status_off();
    menu.close();
    $("#my_info").show();
    socket.emit('get_user', {});

}

function display_news() {
    appRunning = "news";
    display_status_off();
    menu.close();


    $("#news").show();
    socket.emit('get_news', {});
}

