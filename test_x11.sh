#!/bin/bash
export DISPLAY=:0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
export WAYLAND_DISPLAY=wayland-0

touch ~/.Xauthority
xauth add :0 . $(xxd -l 16 -p /dev/urandom) 2>/dev/null || true
export XAUTHORITY=~/.Xauthority

echo "Testing X11 connection..."
echo "DISPLAY=$DISPLAY"
echo "XAUTHORITY=$XAUTHORITY"

python3 << 'EOF'
import os
os.environ['DISPLAY'] = ':0'
import pyautogui
import sys

try:
    size = pyautogui.size()
    pos = pyautogui.position()
    print(f"Screen size: {size}")
    print(f"Current position: {pos}")
    print("X11 forwarding is working!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
