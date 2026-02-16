#!/usr/bin/env python3
import os
os.environ['DISPLAY'] = ':0'
os.environ['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'

from PIL import Image
import subprocess

subprocess.run(['scrot', '/tmp/test.png'], check=True)
img = Image.open('/tmp/test.png')
print('Size:', img.size)
print('Mode:', img.mode)
print('Pixel at 100,100:', img.getpixel((100, 100)))
