#!/usr/bin/env bash

# Tell me first where I am
src="${BASH_SOURCE[0]}"
# resolve $src until the file is no longer a symlink
while [ -h "$src" ]; do 
  dir="$( cd -P "$( dirname "$src" )" && pwd )"
  src="$(readlink "$src")"
  # if $src was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  [[ $src != /* ]] && src="$dir/$src" 
done
dir="$( cd -P "$( dirname "$src" )" && pwd )"

# Now I can call my friends who are just next to me
source "$dir"/cecho.sh
config_parser "$dir"/../config.ini

# Let's check if the virtual environment exists
if [ ! -f $dir/env/bin/python ]; then
  abort "You need to execute setup.sh first"
fi

# Do the stuff
source $dir/env/bin/activate
scrap || { deactivate; abort "Errors ocurred while scrapping facebook. Check the log file"; }
deactivate
info "[INFO]: Very good!"
