#!/bin/bash
while true; do

inotifywait -e modify,create,delete,move -r $1

done