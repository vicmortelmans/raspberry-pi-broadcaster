#!/usr/bin/python3
import threading
import rpb_state_machine
import http_server

if __name__ == "__main__":
    state_machine = rpb_state_machine.RPB_State_Machine()
    http_server.start_server(state_machine)


