from state import State

class IdleState(State):
    """
    The state which indicates that there is no streaming.
    """

    def on_event(self, event):
        if event == 'start' or event == 'button-short':
            return StartingState()
        elif event == 'reboot' or event == 'button-long':
            return RebootingState()

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

        return self
    

class RebootingState(State):
    """
    The state which indicates that the RPB is being rebooted.
    """

    def on_event(self, event):
        if event == 'reboot' or event == 'button-long':
            return RebootingState()

        return self
