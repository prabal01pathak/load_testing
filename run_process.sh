#!/bin/bash

process_count=1
thread_count=1

function runapp() {
  echo "Process Count: $process_count, Thread-count: $thread_count";
  echo "Process Count: $1, Thread-count: $2";
  # gnome-terminal --tab -- bash -c "python3 runapp.py; exec bash";
}


runapp $1 $2 
