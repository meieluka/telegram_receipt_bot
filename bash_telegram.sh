#!/bin/bash

python3 main.py 1>stdout.out 2>stderr.out &

while true
do
    lines=$( wc -l < stderr.out )
    if [ "$lines" -gt "1000" ]; then
        echo "clean"
        echo -n "" > stderr.out
    fi
    sleep 10
done
