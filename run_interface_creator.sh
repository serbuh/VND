#!/bin/bash
# Parse args
while [[ $# -ge 1 ]]
do
  key="$1"
  case $key in

    -c|console)
        console=true
        ARG="$2"
        shift
        ;;
  esac
  shift
done