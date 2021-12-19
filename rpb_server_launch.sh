#!/bin/bash
cd "${0%/*}"
./rpb_server.py 2>&1 | logger
