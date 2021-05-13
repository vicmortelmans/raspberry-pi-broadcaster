import configuration
import logging
import asyncio
import ws_server
import start_broadcasts


def inform_clients(state):
    # Send the state change to the websocket clients
    logging.info("Scheduling task for sending new state to clients")
    asyncio.create_task(ws_server.send_message(str(state)))

def message_clients(html):
    # Send the state change to the websocket clients
    logging.info("Scheduling task for sending new state to clients")
    asyncio.create_task(ws_server.send_message(html))


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

    {"name":"start","data":{"title":"Custom Title","description":"Custom Description"}}
    {"name":"started","data":[{"id":...,"rtmp":...,"ini":"<name of stream in config.ini>","view":"<link to stream for viewing>"},...]}
    {"name":"button-short"}
    {"name":"reboot"}
    {"name":"button-long"}
    """

    def handle(self, event):
        if event['name'] == 'start' or event['name'] == 'button-short':
            if not 'data' in event:
                raise KeyError("no 'data' in event")
            data = {
                    'title': '',
                    'description': '',
                    'password': ''
                    }
            data.update(event['data'])  # fallback values
            configuration.check_password(data['password'])  # throw error if password is wrong
            new_state = StartingState()
            logging.info("New state is " + str(new_state))
            logging.info(f"Scheduling task for starting the livestream with data: '{str(data)}'")
            # Start the broadcasting in a task
            task = asyncio.create_task(start_broadcasts.async_start(data['title'], data['description']))
            # The task returns an event!
            # Handle the event in a task
            asyncio.create_task(Machine().await_event(task))

            inform_clients(new_state)
            return new_state

        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            inform_clients(new_state)
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class StartingState(State):
    """
    The state which indicates that streaming is attempted to be started.
    """

    def handle(self, event):
        if event['name'] == 'started':
            if not 'data' in event:
                raise KeyError("no 'data' in event")
            new_state = StreamingState()
            logging.info("New state is " + str(new_state))

            inform_clients(new_state)
            message_clients()
            return new_state

        elif event['name'] == 'failed':

            inform_clients(new_state)
            return IdleState()

        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            inform_clients(new_state)
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class StreamingState(State):
    """
    The state which indicates that streaming is ongoing.
    """

    def handle(self, event):
        if event['name'] == 'stop':
            new_state = StoppingState()
            logging.info("New state is " + str(new_state))
            logging.info(f"Scheduling task for stopping the livestream")
            task = asyncio.create_task(start_broadcasts.async_stop())
            asyncio.create_task(Machine().await_event(task))

            inform_clients(new_state)
            return new_state

        elif event['name'] == 'streaming-died':

            inform_clients(new_state)
            return IdleState()
        
        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            inform_clients(new_state)
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class StoppingState(State):
    """
    The state which indicates that streaming is being ended.
    """

    def handle(self, event):
        if event['name'] == 'stopped':

            inform_clients(new_state)
            return IdleState()

        elif event['name'] == 'reboot' or event['name'] == 'button-long':

            inform_clients(new_state)
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class RebootingState(State):
    """
    The state which indicates that the RPB is being rebooted.
    """

    def handle(self, event):
        if event['name'] == 'reboot' or event['name'] == 'button-long':

            inform_clients(new_state)
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


# https://dev.to/karn/building-a-simple-state-machine-in-python

