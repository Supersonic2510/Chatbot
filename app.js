// Supports ES6 (Venom official code)
// import { create, Whatsapp } from 'venom-bot';
const venom = require('venom-bot');
var request = require('request');
const {response} = require("express");

var userResponse;
var userRequest;
var user;

// create instance of whatsapp web
var session = venom
  .create({
    session: 'session-name', //name of session
    multidevice: false
  });

session.then((client) => start(client))
    .catch((erro) => {
    console.log(erro);
  });

// send via POST the message from the user to chatbot.
function start(client) {
  client.onMessage((message) => {
    if (message.isGroupMsg === false) {
        console.log("Console ID" + message.from)
        user = message.from;
        request({
            headers: {'content-type': 'application/json'},
            url: 'http://localhost:3030',
            body: {
                "messagePost": message.body,
                "messageID": message.from
            },
            json: true,
            method: "POST"
            }, function (error, response, body){
        });
    }
  });
}

    var app = require("express")();
    var http = require('http').Server(app);
    var bodyParser = require('body-parser');

    // send text answer or image
    app.use(bodyParser.json())
    // get answer from chatbot and sends it to whatsapp with functions send() or sendImage()
    app.post('/',function(req,res){
        if (req.body.messagePython !== undefined) {
            console.log("MessagePython Value: ");
            userResponse = req.body;
            console.log("User request: ", userResponse.messagePython);
            session.then(client => send(client, userResponse.idPython)).
            catch((erro) => {
                console.log(erro);
            });
            res.end();
        }else if (req.body.messageImageFile !== undefined) {
            console.log("MessageImageFile Value: ");
            userResponse = req.body;
            console.log("User request: ", userResponse.messageImageFile);
            session.then(client => sendImage(client, userResponse.idPython)).
            catch((erro) => {
                console.log(erro);
            });
            res.end();
        }
    });


    app.get('/',function(req,res){
        res.body = userResponse
        console.log("User response: ", userResponse);
        res.end();
    });

    http.listen(3000, function(){
        console.log('listening...');
    });


function send(client, id) {
    client
        .sendText(id, userResponse.messagePython)
        .then((result) => {
          //console.log('Result: ', result); //return object success
        })
        .catch((erro) => {
          console.error('Error when sending: ', erro); //return object error
        });
}

function sendImage(client, id) {
    // Bug current Whatsapp API version (instead of sending image, we send text only)
    client
        .sendImage(id, userResponse.messageImageFile, userResponse.messageImageName, userResponse.messageImageCaption)
        .then((result) => {
          //console.log('Result: ', result); //return object success
        })
        .catch((erro) => {
          console.error('Error when sending: ', erro); //return object error
        });
}