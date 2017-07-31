'use strict';
var http = require('http');
var fs = require('fs');
var readConfig = require('read-config');
var spawn = require("child_process").spawn;

var clientFromConnectionString = require('azure-iot-device-amqp').clientFromConnectionString;
var Message = require('azure-iot-device').Message;

var config = readConfig('./config.json');
console.log('config=' + JSON.stringify(config));
var fileLoccation = "~/Documents/opencv/samples/pycam/data.xml";
//var connectionString = 'HostName={host}.azure-devices.net;DeviceId={id};SharedAccessKey={key}';
var connectionString = config.iotHubConnectionString;

console.log(connectionString);
var client = clientFromConnectionString(connectionString);

function printResultFor(op) {
    return function printResult(err, res) {
        if (err) console.log(op + ' error: ' + err.toString());
        if (res) console.log(op + ' status: ' + res.constructor.name);

    };
}

function downloadHaarCascade(url, file){
	var stream = fs.createWriteStream(file,{flags:"w"});
	var request = http.get(url, function(resp){
		resp.pipe(stream);
	});
}

var child_process = null;

var connectCallback = function (err) {
    if (err) {
        console.log('Could not connect: ' + err);
    } else {
        console.log('Client connected');
        client.on('message', function (msg) {
            client.complete(msg, printResultFor('completed'));
            console.log('Id: ' + msg.messageId + ' Body: ' + msg.data);
            var cmd = JSON.parse(msg.data);
            console.log('### cmd = ' + cmd.name);
            switch (cmd.name) {
                case 'cmd_takepic':
                    child_process = spawn('raspistill',['-o','test.jpg']);
                    console.log('taking picture......');
                    client.complete(msg, printResultFor('completed'));
                    break;
		case 'updateHaarCascade':
			var url = cmd.url;
			downloadHaarCascade(url, fileLocation);
                case 'cmd_streaming':
                    break;
                case 'cmd_shutdown':
                    break;
            }
        });
        function random (low, high) {
            return Math.random() * (high - low) + low;
        }
        function randomIntInc (low, high) {
            return Math.floor(Math.random() * (high - low + 1) + low);
        }
        // Create a message and send it to the IoT Hub every second
        setInterval(function () {
            //heartbeat
            var data = JSON.stringify(
                    { 
                        Temperature: random(30,35),
                        Pressure:random(800,820),
                        Timestamp:new Date(),
                        Fanspeed:randomIntInc(1200,1250),
                        WaterLevel:random(80,85)
                    });
            var message = new Message(data);
            console.log("Sending message: " + message.getData());
            client.sendEvent(message, printResultFor('send'));

        }, 3000);
    }
};
client.open(connectCallback);
