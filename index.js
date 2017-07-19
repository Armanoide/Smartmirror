var express = require('express');
var app = express();
var server = require('http').Server(app);
var io = require('socket.io')(server);
var request = require('request');

var port = 3000;

app.use(express.static('./public'));

server.listen(port);


app.get('/', function (req, res) {
    res.sendFile(__dirname + '/public/home.html');
});

var state  = "IN_USE";
var position_hand_vertical = "";
var position_hand_horizontal = "";
var count_circle_convex = 0;
var hsv_img;


// url https://api.weather.com/v2/turbo/vt1observation?apiKey=d522aa97197fd864d36b418f39ebb323&geocode=48.8126242%2C2.3706434&units=m&language=fr-FR&format=json


io.on('connection', function (socket) {


    io.emit('state', {'state': state});

    socket.on('set_hsv_img', function (data) {
        hsv_img = data.hsv_img;

        //in case we have base64 b'b"/9dsfdfdsffs=''
        if (hsv_img[0] === 'b') {
            hsv_img = hsv_img.substring(4);
            hsv_img = hsv_img.substring(0, hsv_img.length - 2);
        }
        socket.broadcast.emit('hsv_img', {'hsv_img': hsv_img  });
    });

    socket.on('set_status', function (data) {
        state  = data.status.split('.')[1];
        socket.broadcast.emit('state', {'state': state  });
    });

    socket.on('get_state', function () {
        socket.emit({'state': state });
    });

    socket.on('set_count_circle_convex', function (data) {
        count_circle_convex = data.count_circle_convex;
        socket.broadcast.emit('count_circle_convex',
            {'count_circle_convex': count_circle_convex });
    });

    socket.on('set_position_hand_horizontal', function (data) {
        position_hand_horizontal = data.position_hand_horizontal.split('.')[1];
        socket.broadcast.emit('position_hand_horizontal',
            {'position_hand_horizontal': position_hand_horizontal });
    });

    socket.on('set_position_hand_vertical', function (data) {
        position_hand_vertical = data.position_hand_vertical.split('.')[1];
        socket.broadcast.emit('position_hand_vertical',
            {'position_hand_vertical': position_hand_vertical });
    });


    socket.on('get_weather', function () {

        request('http://164.132.226.172:8080/api/v1/users/me/weather', function (error, response, body) {
            if (!error && response.statusCode == 200) {
                socket.emit('weather', body);
            } else {

            }
        });
    });

    socket.on('get_news', function () {

        request('https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey=637c55c4fcbc41b683758dac200bc450&category=technology', function (error, response, body) {
            if (!error && response.statusCode == 200) {
                socket.emit('news', body);
            } else {

            }
        })

    });

    socket.on('get_me', function () {

        request('http://164.132.226.172:8080/api/v1/users/me', function (error, response, body) {
            if (!error && response.statusCode == 200) {
                socket.emit('user', body);
            } else {

            }
        });
    });

});
