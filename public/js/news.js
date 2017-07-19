/**
 * Created by norbert on 19/07/2017.
 */

var News = function (socket) {

    var instance = this;
    var callbackEvent;
    instance.news = null;

    socket.on('news', function (data) {

        if ("string" == typeof (data)) {
            instance.news = JSON.parse(data);
        }

        instance.news = instance.news.articles;

        callbackEvent(instance.news);

    });

    this.on = function(callback){
        callbackEvent = callback;
    }

};