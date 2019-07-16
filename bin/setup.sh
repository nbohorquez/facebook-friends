#!/usr/bin/env bash

create_env() {
  alias rollback="rm -rf $dir/env 2>/dev/null; return 1"

  if [ ! -f "$dir"/env/bin/python ]; then
    virtualenv "$dir"/env 2>&1 || rollback
  fi

  source "$dir"/env/bin/activate
  cdir=`pwd`
  config.section.project
  cd "$base_dir"
  python setup.py develop 2>&1 || { cd "$cdir"; deactivate; }
  cd "$cdir"
  deactivate

  return 0
}

create_db() {
  source "$dir"/env/bin/activate
  load_constants || return 1
  deactivate
}

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

# Let's create a virtual environment to isolate this execution environment
create_env || abort "Could not create python virtual environment"
info "[INFO]: Virtual environment created"

# Let's create the database
create_db || abort "Could not create database"
info "[INFO]: Database created"
