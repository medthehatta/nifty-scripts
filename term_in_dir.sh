#!/bin/bash

# If the first arg is a dir, use that dir
#  and assume the name is the dir base
# If the first arg is NOT a dir, use $HOME
#  and assume the name is the first arg
if [ -d "$1" ]; then
  WHERE="$1"
  NAME=$(basename "$1")
else
  WHERE="$HOME"
  NAME="$1"
fi

cd "$WHERE"

# Read in the second argument
# If it exists, it's specifying the name
shift
if (( "$#" )); then
  NAME="$1"
fi

# Launch tmux in the directory with the given name
urxvt -e tmux new -A -s "$NAME"

