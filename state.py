import logging
import asyncio
import ws_server
import start_broadcasts

# https://dev.to/karn/building-a-simple-state-machine-in-python


class RPB_State_Machine(object):
    """ 
    Raspberry Pi Broadcaster State Machine
    """

    def __init__(self):
        """ Initialize the components. """

        # Start with a default state.
        self.state = IdleState()

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.

        Events are dicts with at least a name property and optionally additional info
        """
        try:
            if not 'name' in event:
                raise KeyError("no 'name' in event")

            logging.info(f"State machine in state '{self.state}' receiving event '{event['name']}'")

            # The next state will be the result of the on_event function.
            # If the on_event() method raises an exception, the state is NOT changed !!
            self.state = self.state.on_event(event)
            logging.info(f"State machine has a new state: '{self.state}'")
        except KeyError as e:
            logging.error(f"Missing data in event: '{event}' ({e})")


class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    def __init__(self):
        logging.info(f"Processing current state '{str(self)}'")

    def on_event(self, event):
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
    """

    def on_event(self, event):
        if event['name'] == 'start' or event['name'] == 'button-short':
            if not 'data' in event:
                raise KeyError("no 'data' in event")
            data = {
                    'title': '',
                    'description': ''
                    }
            data.update(event['data'])
            new_state = StartingState()
            logging.info("New state is " + str(new_state))
            logging.info("Scheduling task for sending new state to clients")
            asyncio.create_task(ws_server.send_message(str(new_state)))
            logging.info(f"Scheduling task for starting the livestream with data: '{str(data)}'")
            asyncio.create_task(start_broadcasts.async_start(data['title'], data['description']))
            return new_state
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class StartingState(State):
    """
    The state which indicates that streaming is attempted to be started.
    """

    def on_event(self, event):
        if event == 'started':
            return StreamingState()
        elif event == 'failed':
            return IdleState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class StreamingState(State):
    """
    The state which indicates that streaming is ongoing.
    """

    def on_event(self, event):
        if event == 'stop':
            return StoppingState()
        elif event == 'streaming-died':
            return IdleState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class StoppingState(State):
    """
    The state which indicates that streaming is being ended.
    """

    def on_event(self, event):
        if event == 'stopped':
            return IdleState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


class RebootingState(State):
    """
    The state which indicates that the RPB is being rebooted.
    """

    def on_event(self, event):
        if event == 'reboot' or event == 'button-long':
            return RebootingState()

        logging.error(f"Unexpected event, state is not changed")
        return self


