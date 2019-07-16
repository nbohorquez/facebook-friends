#!/usr/bin/env bash

<<MILLIJIGUI
# Config parser taken from:
# http://theoldschooldevops.com/2008/02/09/bash-ini-parser/ 
cfg_parser () {
  OLD_IFS="$IFS"
  ini="$(<$1)"                # read the file
  ini="${ini//[/\[}"          # escape [
  ini="${ini//]/\]}"          # escape ]
  IFS=$'\n' && ini=( $ini ) # convert to line-array
  ini=( ${ini[*]//;*/} )      # remove comments with ;
  ini=( ${ini[*]/\	=/=} )    # remove tabs before =
  ini=( ${ini[*]/=\	/=} )     # remove tabs after =
  ini=( ${ini[*]/\ =/=} )     # remove space before =
  ini=( ${ini[*]/=\ /=} )     # remove space after =
  ini=( ${ini[*]/#\\[/\}$'\n'cfg.section.} ) # set section prefix
  ini=( ${ini[*]/%\\]/ \(} )  # convert text2function (1)
  ini=( ${ini[*]/=/=\( } )    # convert item to array
  ini=( ${ini[*]/%/ \)} )     # close array parenthesis
  ini=( ${ini[*]/%\\ \)/ \\} ) # the multiline trick
  ini=( ${ini[*]/%\( \)/\(\) \{} ) # convert text2function (2)
  ini=( ${ini[*]/%\} \)/\}} ) # remove extra parenthesis
  ini[0]="" # remove first element
  ini[${#ini[*]} + 1]='}'     # add the last brace
  eval "$(echo "${ini[*]}")"  # eval the result
  IFS="$OLD_IFS"
}

cfg_writer () {
  IFS=' '$'\n'
  fun="$(declare -F)"
  fun="${fun//declare -f/}"
  for f in $fun; do
    [ "${f#cfg.section}" == "${f}" ] && continue
    item="$(declare -f ${f})"
    item="${item##*\{}"
    item="${item%\}}"
    item="${item//=*;/}"
    vars="${item//=*/}"
    eval $f
    echo "[${f#cfg.section.}]"
    for var in $vars; do
      echo $var=\"${!var}\"
    done
  done
}

parse_config() {
  if [ ! -f "$1" ]; then
    error "[ERROR]: File $1 does not exist"
    return 1
  fi

  # Hay muchas formas de leer un config file sin usar source:
  # http://stackoverflow.com/questions/4434797/read-a-config-file-in-bash-without-using-source
  while read line; do
  if [[ "$line" =~ ^[^#]*= ]]; then
    variable=`echo $line | cut -d'=' -f 1 | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'`
    value=`echo $line | cut -d'=' -f 2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'`
    eval "$variable"="'$value'"
  fi
  done < "$1"
}
MILLIJIGUI
