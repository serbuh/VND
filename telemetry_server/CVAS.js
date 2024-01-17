// telemetry source object for the CVAS

const dgram = require('dgram');
const server = dgram.createSocket('udp4');
const fs = require('fs');

function CVAS() {

	
	// Initialize working Parameters and Object

	// read the keys from dictionary (of the compiled openmct)
	let rawDict = fs.readFileSync('../openmct/dist/telemetry_plugin/openmct_interface.json')
	let input_port = parseInt(fs.readFileSync('port_config.txt', "utf8"));
	let dict = JSON.parse(rawDict)
	//console.log(dict.measurements.map(obj => obj.key))

	this.state={};
	(dict.measurements.map(obj => obj.key)).forEach(function (k) {
		this.state[k] = 0;
	}, this);
	//console.log(this.state)

    this.history = {}; //history object
    this.listeners = [];
	this.data = []; // temporar data array
	this.continousLogging = false; //whether continous logging is used
	this.FileTimestamp = '';

	// keys initialized in the history object
	Object.keys(this.state).forEach(function (k) {
        this.history[k] = [];
		console.log(k);
	}, this);

	// to notify telemetry server interval based (STFE) uncomment here
    setInterval(function () {
        this.generateIntervalTelemetry();
    }.bind(this), 100); //z.B. 100ms according to SFTE

    var count = 0 //for calculations
	var initGPSheight = 0; //for calculations

	//what to do, when a message from the UDP Port arrives
    server.on('message', (msg, rinfo) => {
		//console.log(`\nNew msg from ${rinfo.address}:${rinfo.port}:\n${msg}`)
		
		// Iterate through fields (key, value) in current dict
		const json_parsed = JSON.parse(msg);
		for (let new_line_orig of Object.keys(json_parsed)) {
			// Replace spaces with underscores
			key_name = new_line_orig.replaceAll(" ", "_");
			
			// Parse a key name for OpenMCT
			var key;
			if (new_line_orig.includes(".")) {
				// New format: section.key: (val, color)
				key = key_name;
			} else {
				// Old format: key: (val, section, color)
				section_name = json_parsed[new_line_orig][1].replaceAll(" ", "_");
				key = section_name + "." + key_name;
			}
			
			// Parse value and give a timestamp
			const value = json_parsed[new_line_orig][0];
			const timestamp = Date.now(); // internal JS timestamp [ms]
			
			// Ignore undefined keys
			if (!(key in this.history)) {
				console.log("* undefined: " + key);
				continue;
			}

			// Log new line
			console.log(key + " : " + value + " (" + timestamp + ")")
		
			//Save the data to the state array
			this.state[key] = value;
			this.state['Time.stamp'] = timestamp

			//// to notify telemetry server every time new data arrives in uncomment here and comment the interval based approach
			//this.generateRealtimeTelemetry();

			//// Save History on every message, for highest possible resolution
		
			// built message
			var message = { timestamp: timestamp, value: this.state[key], id: key};
				try{ // store in history
					this.history[key].push(message);
					//console.log(this.history[this.data[0]])
					
					// if continous logging is activated, append message to log file
					if(this.continousLogging){					
			
						//Using Promises for less interrupting the main loop
						this.asyncStringyify(message).then(function(write) {//write is the value of the resolved promise in asyncStringify
							fs.appendFile(__dirname + '/saved_logs/CVAS_'+this.FileTimestamp+'_rawMessage.json', write, (err) => {
								if (err) {
									console.log(err);
								} 
							}) 
						}.bind(this));

					}	
					} catch (e) {
						console.log(e)
					}
		}

	});
	
	server.on('error', (err) => {
		console.log(`CVAS UDP server error:\n${err.stack}`);
		try{
			console.log('Try to reconnect...')
			server.bind(input_port);
		} catch(e) {
			console.log('Reconnect Failed...')
			console.log(e)
			server.close()
		}
		
	});

	// port specified in the associated python script
	server.bind(input_port);

    console.log("\nTelemetry server initialized. Listening on port : " + input_port + "\n");
};


// to update every time new data comes in
CVAS.prototype.generateRealtimeTelemetry = function () {

	// Real Timestamp
	var timestamp = this.state['Time.stamp'];
	// Artificial timestamp
	//var timestamp= Date.now();

	// built message
	var message = { timestamp: timestamp, value: this.state[this.data[0]], id: this.data[0]};
	// notify realtimeserver
	this.notify(message);
	//console.log(message);

}


// to update interval based (STFE)
CVAS.prototype.generateIntervalTelemetry = function () {

    Object.keys(this.state).forEach(function (id) {

        // Real Timestamp
		var timestamp = this.state['Time.stamp'];
		// Artificial timestamp
        //var timestamp= Date.now();

		// built message
		var message = { timestamp: timestamp, value: this.state[id], id: id};
		// notify realtimeserver
        this.notify(message);
		
	}, this);
	//console.log(state);
};


// notifiy function, called in generate Telemetry, notifies listeners
CVAS.prototype.notify = function (point) {
    this.listeners.forEach(function (l) {
        l(point);
    });
};


// manages listeners for realtime telemetry
CVAS.prototype.listen = function (listener) {
    this.listeners.push(listener);
    return function () {
        this.listeners = this.listeners.filter(function (l) {
            return l !== listener;
        });
    }.bind(this);
};

// Creating a File Timestamp 
CVAS.prototype.SetFileTimestamp = function () {

	//zero needed for right time and date format when copy-pasting in OpenMCT
	addZero = function(dateNumber) {
		if (dateNumber.toString().length == 1){
			dateNumber = '0'+dateNumber.toString()
		}
		return dateNumber
	}
	//Generate timestamp for the File
	var date = new Date();
	var year = date.getFullYear();
	var month = addZero(date.getMonth() + 1);      // "+ 1" because the 1st month is 0
	var day = addZero(date.getDate());
	var hour = addZero(date.getHours());
	var minutes = addZero(date.getMinutes());
	var seconds = addZero(date.getSeconds());
	this.FileTimestamp = year+ '-'+ month+ '-'+ day+ ' '+ hour+ '-'+ minutes+ '-'+ seconds;

};

//asynchronous Strigify an object/a variable to JSON format
CVAS.prototype.asyncStringyify = function (obj) {
	return new Promise((resolve, reject) => {
	  resolve(JSON.stringify(obj));
	});
  }



// what to do on incoming command
CVAS.prototype.command = function (command) {

	// Logs the history variable (this.history) once
	if(command === ':saveHistory'){
		
		
		this.SetFileTimestamp()

		//Using Promises for not interrupting the main loop
		function asyncSaveHistory(str) {
			return new Promise((resolve, reject) => {
			  resolve(JSON.stringify(str));
			});
		  }

		this.asyncStringyify(this.history).then(function(write) {//write is the value of the resolved promise in asyncStringify
			fs.writeFile(__dirname + '/saved_logs/CVAS_'+this.FileTimestamp+'_History.json', write, (err) => {
				if (err) {
					console.log(err);
				} else {
				console.log('History Saved!')
				}
			}) 
		}.bind(this));
	
	};


	// Logs the history variable (this.history) every 10s
	// because of the structure of this.history, with the current logic the file has to be rewritten on every save
	// due to this, a lot of performance is needed, especially on long recordings >20min with a lot of data (40 telemetry points @10Hz)
	// not recommended, instead save the history at the end of the test with the "saveHistory" command on log only messages continously, so secure the data

	// if(command === ':startcontinousHistoryLog'){
		
	// 	this.SetFileTimestamp()

	// 	Using Promises for not interrupting the main loop
	// 	function asyncLogging(src) {
	// 		return new Promise((resolve, reject) => {
				
	// 		  resolve(JSON.stringify(src));
	// 		});
	// 	  }
		
	
	// 	save log in specified interval
	// 	logging = setInterval(function () {
	// 		asyncLogging(this.history).then(function(write) {//write is the value of the resolved promise in asyncStringify
	// 			fs.writeFile(__dirname + '/saved_logs/CVAS_'+this.FileTimestam+'.json', write, (err) => {
	// 				if (err) {
	// 					throw err;
	// 				}
	// 				console.log(this.history);
	// 				console.log('Logging!')
	// 			}) 
	// 		}.bind(this));
	// 	}.bind(this), 10000); 
	
			
	// };


	// if(command === ':endContinousHistoryLog'){
	// 	clearInterval(logging);
	// 	console.log('Logging stopped!')	
	// };


	// for continous logging use this method, saved file can not be used in OpenMCT as is, but all data is stored more efficiently 
	if(command === ':startLog'){

		this.SetFileTimestamp()

		this.continousLogging = true;
		console.log('Logging started!')	
	};

	if(command === ':endLog'){
		this.continousLogging = false;
		console.log('Logging stopped!')	
	};


	// Example implementation of sending a command
	if(command === ':exampleCommandtoPlane'){
		// sending to the specified udp port on the address 'loacalhost'
		server.send(command,50021, 'localhost')
		console.log('Command Sent via UDP Port!')	
	};

	
};


module.exports = function () {
    return new CVAS()
};
