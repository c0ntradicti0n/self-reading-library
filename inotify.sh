#!/bin/bash
apt update
apt install -y inotify-tools
while true; do

  inotifywait --quiet -e modify,create,delete,move -r $1

done