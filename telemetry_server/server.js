// main file of the telemtry server, comment/uncomment what is needed

//import the objects

var RealtimeServer = require('./realtime-server');
var HistoryServer = require('./history-server');
var HistoryReader = require('./history_reader');
var CVAS = require('./CVAS')
var expressWs = require('express-ws');
var app = require('express')();
expressWs(app);

// initialize the objects

var CVAS_inst = new CVAS;
var historyReader = new HistoryReader;
var realtimeServerCVAS = new RealtimeServer(CVAS_inst);
var historyServerCVAS = new HistoryServer(CVAS_inst);

// use the objects

var historyServerReader = new HistoryServer(historyReader);

app.use('/CVASRealtime', realtimeServerCVAS);
app.use('/CVASHistory', historyServerCVAS);
app.use('/HistoryReader', historyServerReader);

// start the server
var port = process.env.PORT || 16969
app.listen(port)
