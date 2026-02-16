#!/bin/bash
export DISPLAY=:0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir

echo "Test copy:"
echo "Hello Test" | xclip -selection clipboard

echo "Test paste:"
xclip -selection clipboard -o
