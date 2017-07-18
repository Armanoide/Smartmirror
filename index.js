var express = require('express');
var app = express();
var server = require('http').Server(app);
var io = require('socket.io')(server);

var port = 3000;

app.use(express.static('./public'));

server.listen(port);


app.get('/', function (req, res) {
    res.sendFile(__dirname + '/public/home.html');
});

var state  = "OFF";
var position_hand_vertical = "";
var position_hand_horizontal = "";
var count_circle_convex = 0;
var hsv_img;


// url https://api.weather.com/v2/turbo/vt1observation?apiKey=d522aa97197fd864d36b418f39ebb323&geocode=48.8126242%2C2.3706434&units=m&language=fr-FR&format=json
var fakeDataWeather = {
    "id": "48.8126242,2.3706434",
    "vt1observation":
        {
            "altimeter":1016.26,
            "barometerTrend":"En baisse",
            "barometerCode":2,
            "barometerChange":-0.68,
            "dewPoint":16,
            "feelsLike":21,
            "gust":null,
            "humidity":72,
            "icon":32,
            "observationTime":"2017-07-18T07:58:40+0200",
            "obsQualifierCode":null,
            "obsQualifierSeverity":null,
            "phrase":"Ensoleillé",
            "precip24Hour":0.0,
            "snowDepth":0.0,
            "temperature":21,
            "temperatureMaxSince7am":21,
            "uvIndex":0,
            "uvDescription":"Faible",
            "visibility":16.09,
            "windSpeed":10,
            "windDirCompass":"NE",
            "windDirDegrees":40
        }
};

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
        socket.emit('weather', fakeDataWeather);
    });

});
