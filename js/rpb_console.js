// Initiate websocket connection
const socket = new WebSocket('wss:/' + window.location.host + '/socket.io/');

// Listen for messages
socket.addEventListener('message', function (event) {
    const state = event.data;
    console.log('Message from server ', state);
    if (["IdleState","StartingState","StreamingState","StoppingState","RebootingState"].includes(state)) {
        // hide/show dynamic elements
        hideShowDynamicItems(state);
        // remove previous message
        document.querySelector("#status-error p").innerHTML = "";
    } else {
        // just display it as a message
        document.querySelector("#status-error p").innerHTML = state;
    }
});

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
	socket.send(JSON.stringify(message));
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
	socket.send(JSON.stringify(message));
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

