// Initiate websocket connection
const socket = new WebSocket('wss:/' + window.location.host + '/socket.io/');

// Listen for messages
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});

const start_form = document.querySelector('#start-button form');
start_form.addEventListener('submit', event => {
	event.preventDefault();
	const data = new FormData(this);
	const message = {
		"name": "start",
		"data": {
			"title": data.get("title"),
			"description": data.get("description")
		}
	};
	socket.send(JSON.stringify(message));
});
