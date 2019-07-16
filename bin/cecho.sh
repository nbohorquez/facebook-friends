#!/bin/bash

# Tomado de http://tldp.org/LDP/abs/html/colorizing.html
black='\E[30m'
red='\E[31m'
green='\E[32m'
yellow='\E[33m'
blue='\E[34m'
magenta='\E[35m'
cyan='\E[36m'
white='\E[37m'
bold='\E[1m'

cecho() {
  local default_msg="No message to show"

  message=${1:-$default_msg}   # Defaults to default message.
  color=${2:-$black}           # Defaults to black, if not specified.

  echo -ne "$color""$bold""$message"
  echo -e "\E[0m"
  tput sgr0

  return
}

info() {
  cecho "$1" "$green"
}

warning() {
  cecho "$1" "$yellow"
}

debug() {
  cecho "$1" "$blue"
}

error() {
  cecho "$1" "$red"
}

abort() {
  error "[FATAL]: $1. Aborting"
  exit 1
}
