#!/bin/bash
echo "Stop screens..."
killall --wait screen
sleep 1
echo "Stop remaining processes..."
killall --wait /usr/bin/python
