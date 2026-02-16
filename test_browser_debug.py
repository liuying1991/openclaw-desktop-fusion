#!/usr/bin/env python3
import subprocess
import os
import json

env = os.environ.copy()
env['DISPLAY'] = ':0'
env['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'
env['HOME'] = os.path.expanduser('~')

params = {"url": "https://example.com", "headless": True}
with open('/mnt/c/tmp/browser_params.json', 'w') as f:
    json.dump(params, f)

print("Testing browser...")

process = subprocess.Popen(
    ['node', '/mnt/c/tmp/browser_win.js', 'open', '/mnt/c/tmp/browser_params.json'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
)

try:
    stdout, stderr = process.communicate(timeout=30)
    print("Return code:", process.returncode)
    print("Stdout:", stdout[:500] if stdout else 'empty')
    print("Stderr:", stderr[:500] if stderr else 'empty')
except subprocess.TimeoutExpired:
    process.kill()
    stdout, stderr = process.communicate()
    print("TIMEOUT after 30 seconds")
    print("Partial stdout:", stdout[:500] if stdout else 'empty')
    print("Partial stderr:", stderr[:500] if stderr else 'empty')
