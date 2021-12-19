import asyncio
import configuration
import jinja2
import logging
import os
import start_broadcasts
import ws_server

def require_data(event, defaults={}):
    # Raise an error if there's no data
    if not 'data' in event:
        raise KeyError("no 'data' in event")
    if defaults:
        data = defaults
        data.update(event['data'])
    else:
        data = event['data']
    return data

def require_password(data):
    # Raise an error if the password is not correct
    configuration.check_password(data['password'])  # throw error if password is wrong
    return

def inform_clients(state):
    # Send the state change to the websocket clients
    logging.info("Scheduling task for sending new state to clients")
    asyncio.create_task(ws_server.send_message(str(state)))
    return

def message_clients(html):
    # Send a message to the websocket clients
    logging.info("Scheduling task for sending a message to clients")
    asyncio.create_task(ws_server.send_message(html))
    return



class Machine(object):
    """ 
    Raspberry Pi Broadcaster State Machine
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            logging.info("Creating new instance of state machine")
            cls.instance = super(Machine, cls).__new__(cls)
            logging.info("Initializing the state machine with IdleState")
            cls.instance.state = IdleState()
        return cls.instance

    def has_state(self, state_class):
        """ Test current state """
        return isinstance(self.state, state_class)

    def state_string(self):
        """ Return current state as string """
        return str(self.state)

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.

        Events are dicts with at least a name property and optionally additional info

        {"name": "...", "data": {...}}
        """
        try:
            if not 'name' in event:
                raise KeyError("no 'name' in event")

            logging.info(f"State machine in state '{self.state}' receiving event '{event['name']}'")
            # The next state will be the result of the handle function.
            # If the handle() method raises an exception, the state is NOT changed !!
            self.state = self.state.handle(event)
            logging.info(f"State machine has a new state: '{self.state}'")
        except KeyError as e:
            logging.error(f"Missing data in event: '{event}' ({e})")
        except configuration.PasswordError as e:
            logging.error(f"Wrong password in event: '{event}'")
            # ws_server will send following message to the sending client only:
            return "Wrong password!"


    async def await_event(self, task):
        """
        Await the result of the task, which is an event dict. Use this in the event handler when it
        has tasks that don't return instantanuously:

        task = asyncio.create_task(async_function_that_takes_long_and_returns_event_dict())
        asyncio.create_task(Machine().await_event(task))

        """
        logging.info("Awaiting event...")
        event = await task
        logging.info(f"Awaited event '{str(event)}'")
        self.on_event(event)


class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    def __init__(self):
        logging.info(f"Processing current state '{str(self)}'")

    def handle(self, event):
        """
        Handle events that are delegated to this State.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__


class IdleState(State):
    """
    The state which indicates that there is no streaming.

    Examples of events that are accepted:

    {"name":"start","data":{"password":"xxx","title":"Custom Title","description":"Custom Description"}}
    {"name":"button-short"}
    {"name":"reboot","data":{"password":"xxx"}}
    {"name":"button-long"}
    """

    def handle(self, event):
        if event['name'] == 'start':
            data = require_data(event, defaults={'title': '', 'description': '', 'password': ''})
            # fallback values from config.ini file are filled in by create_*_broadcast.py
            require_password(data)

            new_state = StartingState()

            logging.info("New state is " + str(new_state))
            logging.info(f"Scheduling task for starting the livestream with data: '{str(data)}'")
            # Start the rtmp broadcasting in a task
            task = asyncio.create_task(start_broadcasts.async_start(data['title'], data['description']))
            # The task returns a 'started' event that contains a list of active channels!
            # Handle the event in a task
            asyncio.create_task(Machine().await_event(task))

            inform_clients(new_state)
            return new_state

        if event['name'] == 'button-short':

            new_state = StartingState()

            logging.info("New state is " + str(new_state))
            logging.info(f"Scheduling task for starting the livestream using the button")
            # Start the rtmp broadcasting in a task
            task = asyncio.create_task(start_broadcasts.async_start('', ''))
            # Fallback values for title and description from config.ini file 
            # are filled in by create_*_broadcast.py
            # The task returns a 'started' event that contains a list of active channels!
            # Handle the event in a task
            asyncio.create_task(Machine().await_event(task))

            inform_clients(new_state)
            return new_state

        elif event['name'] == 'reboot' or event['name'] == 'button-long':
        
            if event['name'] == 'reboot':
                data = require_data(event, defaults={ 'password': '' })
                require_password(data)

            new_state = RebootingState()

            os.system('./halt.sh')

            inform_clients(new_state)
            return new_state

        logging.error(f"Unexpected event, state is not changed")
        return self


class StartingState(State):
    """
    The state which indicates that streaming is attempted to be started.

    Examples of events that are accepted:

    {"name":"started","data":[{"id":...,"rtmp":...,"ini":"<name of stream in config.ini>","view":"<link to stream for viewing>"},...]}
    {"name":"reboot"}
    {"name":"button-long"}
    """

    def handle(self, event):
        if event['name'] == 'started':
            data = require_data(event)

            new_state = StreamingState()
            logging.info("New state is " + str(new_state))
            template = jinja2.Template('{% for stream in data %}<p><a href="{{ stream.view }}" target="_blank">{{ stream.ini }}</a></p>{% endfor %}')
            channels = template.render(data=data)

            inform_clients(new_state)
            message_clients(channels)
            return new_state

        elif event['name'] == 'failed':

            new_state = IdleState()

            inform_clients(new_state)
            return new_state

        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            if event['name'] == 'reboot':
                data = require_data(event, defaults={ 'password': '' })
                require_password(data)

            new_state = RebootingState()

            os.system('./halt.sh')

            inform_clients(new_state)
            return new_state

        logging.error(f"Unexpected event, state is not changed")
        return self


class StreamingState(State):
    """
    The state which indicates that streaming is ongoing.
    """

    def handle(self, event):
        if event['name'] == 'stop':
            data = require_data(event, defaults={ 'password': '' })
            require_password(data)

            new_state = StoppingState()

            logging.info("New state is " + str(new_state))
            logging.info(f"Scheduling task for stopping the livestream")
            # Execute the killing of the broadcasts in a task
            task = asyncio.create_task(start_broadcasts.async_stop())
            # The task returns a 'stopped'!
            # Handle the event in a task
            asyncio.create_task(Machine().await_event(task))

            inform_clients(new_state)
            message_clients("De uitzending is beëindigd.")
            return new_state

        elif event['name'] == 'button-short':

            new_state = StoppingState()

            logging.info("New state is " + str(new_state))
            logging.info(f"Scheduling task for stopping the livestream")
            # Execute the killing of the broadcasts in a task
            task = asyncio.create_task(start_broadcasts.async_stop())
            # The task returns a 'stopped'!
            # Handle the event in a task
            asyncio.create_task(Machine().await_event(task))

            inform_clients(new_state)
            message_clients("De uitzending is beëindigd.")
            return new_state

        elif event['name'] == 'streaming-died':

            new_state = IdleState()

            inform_clients(new_state)
            message_clients("De uitzending is afgebroken!")
            return new_state
        
        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            if event['name'] == 'reboot':
                data = require_data(event, defaults={ 'password': '' })
                require_password(data)

            new_state = RebootingState()

            os.system('./halt.sh')

            inform_clients(new_state)
            return new_state

        logging.error(f"Unexpected event, state is not changed")
        return self


class StoppingState(State):
    """
    The state which indicates that streaming is being ended.
    """

    def handle(self, event):
        if event['name'] == 'stopped':

            new_state = IdleState()

            inform_clients(new_state)
            return new_state

        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            if event['name'] == 'reboot':
                data = require_data(event, defaults={ 'password': '' })
                require_password(data)

            new_state = RebootingState()

            os.system('./halt.sh')

            inform_clients(new_state)
            return new_state

        logging.error(f"Unexpected event, state is not changed")
        return self


class RebootingState(State):
    """
    The state which indicates that the RPB is being rebooted.
    """

    def handle(self, event):
        if event['name'] == 'reboot' or event['name'] == 'button-long':

            if event['name'] == 'reboot':
                data = require_data(event, defaults={ 'password': '' })
                require_password(data)

            new_state = RebootingState()

            os.system('./halt.sh')

            inform_clients(new_state)
            return new_state

        logging.error(f"Unexpected event, state is not changed")
        return self


# https://dev.to/karn/building-a-simple-state-machine-in-python

