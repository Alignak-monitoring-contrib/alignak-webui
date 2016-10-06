#!/bin/csh
echo "Stop Python processes..."
killall python2.7
sleep 10
killall -KILL python2.7
