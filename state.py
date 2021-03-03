import logging
import asyncio

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
        """

        logging.info(f"rpb_state_machine.py on_event(): '{event}' in old state: '{self.state}'")

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(self, event)
        logging.info(f"rpb_state_machine.py on_event(): new state: '{self.state}'")


class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    def __init__(self):
        logging.info(f"state.py __init__(): Processing current state '{str(self)}'")

    def on_event(self, sm, event):
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

    def on_event(self, sm, event):
        if event == 'start' or event == 'button-short':
            asyncio.create_task()
            return StartingState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        return self


class StartingState(State):
    """
    The state which indicates that streaming is attempted to be started.
    """

    def on_event(self, sm, event):
        if event == 'started':
            return StreamingState()
        elif event == 'failed':
            return IdleState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        return self


class StreamingState(State):
    """
    The state which indicates that streaming is ongoing.
    """

    def on_event(self, sm, event):
        if event == 'stop':
            return StoppingState()
        elif event == 'streaming-died':
            return IdleState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        return self


class StoppingState(State):
    """
    The state which indicates that streaming is being ended.
    """

    def on_event(self, sm, event):
        if event == 'stopped':
            return IdleState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

        return self
    

class RebootingState(State):
    """
    The state which indicates that the RPB is being rebooted.
    """

    def on_event(self, sm, event):
        if event == 'reboot' or event == 'button-long':
            return RebootingState()

        return self


