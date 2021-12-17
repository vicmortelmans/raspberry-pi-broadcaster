var HEARTBEAT_INTERVAL = 10000;
var HEARTBEAT_TIMEOUT = 10000;
var RECONNECT_INTERVAL = 1000;
var PING_MESSAGE = '__ping__';


// Initiate websocket connection
function WebSocketKeepAlive(address) {
    var self, heartbeatTimeout;
    self = this;
	self.reconnect = true;
    self.ws = null;

    // first connection attempt
    createWebSocket(address);

    // create a websocket
    function createWebSocket(address) {
        try {
            self.ws = new WebSocket(address);
        }
        catch (e) {
			console.log('Error creating websocket: ' + e.toString());
            self.ws = null;
			console.log('Going to reconnect');
            reconnectSocket();
        }
        if (self.ws) {
			console.log('Websocket created - configuring');
            configureWebSocket();
        }
    }

    // attempt reconnect
    function reconnectSocket() {
		if (self.reconnect) {
			setTimeout(function () {
				createWebSocket(address);
			}, RECONNECT_INTERVAL);
		}
    }

    // configure the websocket for subscription
    function configureWebSocket() {
        self.ws.addEventListener('open', function () {
			console.log('Websocket opened - starting first ping in 10 seconds');
            heartbeatStart();
        });
        self.ws.addEventListener('message', function (event) {
			const state = event.data;
			console.log('Message from server ', state);
			if (state == PING_MESSAGE) {
				console.log('Websocket pong');
				heartbeatStart(); // message will keep alive, restart heartbeat
			} else if (["IdleState","StartingState","StreamingState","StoppingState","RebootingState"].includes(state)) {
				// hide/show dynamic elements
				hideShowDynamicItems(state);
				// remove previous message
				document.querySelector("#status-error p").innerHTML = "";
			} else {
				// just display it as a message
				document.querySelector("#status-error p").innerHTML = state;
			}
        });
        self.ws.addEventListener('error', function (err) {
			console.log('Websocket error: ' + err.toString());
        });
        self.ws.addEventListener('close', function () {
			console.log('Websocket closed - going to reconnect');
            reconnectSocket();
        });
    }

    // start the heartbeat interval
    function heartbeatStart() {
        heartbeatEnd(); // reset any waiting heartbeat
        heartbeatTimeout = setTimeout(function () {
            heartbeat();
        }, HEARTBEAT_INTERVAL);
    }

    // end any currently waiting heartbeat
    function heartbeatEnd() {
        clearTimeout(heartbeatTimeout);
    }

    // send a heartbeat ping
    function heartbeat() {
        try {
			console.log('Websocket ping');
            self.ws.send(PING_MESSAGE);
            heartbeatTimeout = setTimeout(function () {
                heartbeatFail();
            }, HEARTBEAT_TIMEOUT);
        }
        catch (e) {
            heartbeatFail();
        }
      }

    // process heartbeat failure
    function heartbeatFail() {
        try {
			console.log('Websocket heartbeat failure');
            self.ws.close();
        }
        catch (e) {}
    }
}

WebSocketKeepAlive.prototype.getWebSocket = function () {
    return this.ws;
};

WebSocketKeepAlive.prototype.setReconnect = function (reconnect) {
    this.reconnect = reconnect;
};

WebSocketKeepAlive.prototype.killWebSocket = function () {
	this.setReconnect(false);
	if (this.ws) {
		this.ws.close();
	}
};

wska = new WebSocketKeepAlive('wss:/' + window.location.host + '/socket.io/');

const start_form = document.querySelector('#start-button form');
start_form.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const message = {
        "name": "start",
        "data": {
            "title": data.get("title"),
            "description": data.get("description"),
            "password": data.get("password")
        }
    };
    text = JSON.stringify(message);
    console.log('Message to server ', text);
	wska.getWebSocket().send(text);
});

const stop_form = document.querySelector('#stop-button form');
stop_form.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const message = {
        "name": "stop",
        "data": {
            "password": data.get("password")
        }
    };
    text = JSON.stringify(message);
    console.log('Message to server ', text);
	wska.getWebSocket().send(text);
});

function hideShowDynamicItems(state) {
    const dynamicItems = document.querySelectorAll('div[class~="dynamic"]');
    dynamicItems.forEach(item => {
        if (item.classList.contains(state)) {
            item.style.display = "block";
        } else {
            item.style.display = "none";
        }
    });
}

