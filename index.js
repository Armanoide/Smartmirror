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

var status = "";
var position_hand_vertical = "";
var position_hand_horizontal = "";
var count_circle_convex = 0;

io.on('connection', function (socket) {

    socket.on('set_status', function (data) {
        status = data.status;
        socket.broadcast.emit('status', {'status': status });
    });

    socket.on('set_count_circle_convex', function (data) {
        count_circle_convex = data.count_circle_convex;
        socket.broadcast.emit('count_circle_convex',
            {'count_circle_convex': count_circle_convex });
    });

    socket.on('set_position_hand_horizontal', function (data) {
        position_hand_horizontal = data.position_hand_horizontal;
        socket.broadcast.emit('position_hand_horizontal',
            {'position_hand_horizontal': position_hand_horizontal });
    });

    socket.on('set_position_hand_vertical', function (data) {
        position_hand_vertical = data.position_hand_vertical;
        socket.broadcast.emit('position_hand_vertical',
            {'position_hand_vertical': position_hand_vertical });
    });

    socket.on('get_status', function () {
        io.emit({'status': status });
    });
});
