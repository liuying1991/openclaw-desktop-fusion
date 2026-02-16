#!/usr/bin/env python3
import os
import sys
os.environ['DISPLAY'] = ':0'
os.environ['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'

sys.path.insert(0, '/mnt/c/tmp/openclaw-desktop-fusion/skills/fusion-screen/scripts')
import screen

print("Test 1: analyze")
result = screen.analyze({})
print(result)

print("\nTest 2: pixel_at")
result = screen.pixel_at({'x': 100, 'y': 100})
print(result)

print("\nTest 3: screenshot_base64 with region")
result = screen.screenshot_base64({'region': [0, 0, 500, 500]})
print(result)
