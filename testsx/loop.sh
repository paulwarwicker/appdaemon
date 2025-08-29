#!/usr/bin/env bash

# stub only

# set -x

name="baseline"
touch $name

while true; do
  s=10
  while read file; do
    s=20
    echo "$(date -Iseconds) pytest $file --verbose --showlocals $*"
    pytest $file --verbose --showlocals $*
  done < <(find . -newerma $name) # https://stackoverflow.com/questions/1789750/scope-of-variable-in-pipe
  touch $name
  sleep $s
done
