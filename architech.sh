#!/bin/sh

# Copyright (c) 2018 Daniel Reimer

help() {
    echo "
Architech: An Arch Linux Installer
  -v  	   Validate the conf.json file
  -l	   List the available options for a given configuration field
  -i	   Run the installer
" 1>&2
    exit 1
}

while getopts "vli" o; do
    case "${o}" in
        v)
            ./src/validate.py
	    exit 0
            ;;
        l)
            l=${OPTARG}
	    ./src/list.py
	    exit 0
            ;;
	i)
	    i=${OPTARG}
	    ./src/install.py
	    exit 0
	    ;;
        ?)
            help
            ;;
    esac
done
shift $((OPTIND-1))

help
