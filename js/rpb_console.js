// Initiate websocket connection
const socket = new WebSocket('wss:/' + window.location.host + '/socket.io/');

// Listen for messages
socket.addEventListener('message', function (event) {
    const state = event.data;
    console.log('Message from server ', state);
    // hide/show dynamic elements
    const dynamicItems = document.querySelectorAll('div[class~="dynamic"]');
    dynamicItems.forEach(item => {
        console.log(`state ${state} item classes ${item.className}`);
        if (item.classList.contains(state)) {
            console.log("showing");
            item.style.display = "block";
        } else {
            console.log("hiding");
            item.style.display = "none";
        }
    });
});

const start_form = document.querySelector('#start-button form');
start_form.addEventListener('submit', event => {
	event.preventDefault();
	const data = new FormData(event.currentTarget);
	const message = {
		"name": "start",
		"data": {
			"title": data.get("title"),
			"description": data.get("description")
		}
	};
	socket.send(JSON.stringify(message));
});
