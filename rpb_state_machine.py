from rpb_states import IdleState

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

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)
