#!/usr/bin/env python3
import os
os.environ['DISPLAY'] = ':0'
os.environ['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'

import sys
sys.path.insert(0, '/mnt/c/tmp/openclaw-desktop-fusion/skills/fusion-clipboard/scripts')
import clipboard

print("Test copy:")
result = clipboard.copy_text({'text': 'Hello from Python'})
print(result)

print("\nTest get:")
result = clipboard.get_clipboard({})
print(result)

print("\nTest clear:")
result = clipboard.clear_clipboard({})
print(result)
