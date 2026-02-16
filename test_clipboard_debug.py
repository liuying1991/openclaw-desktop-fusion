#!/usr/bin/env python3
import subprocess
import json
import os
import tempfile

env = os.environ.copy()
env['DISPLAY'] = ':0'
env['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'

params = {'text': 'Hello Fusion Clipboard Test'}
params_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(params, params_file)
params_file.close()

print("=== Test Clipboard Copy ===")
result = subprocess.run(
    ['python3', '/mnt/c/tmp/openclaw-desktop-fusion/skills/fusion-clipboard/scripts/clipboard.py', 'copy', params_file.name],
    capture_output=True, text=True, timeout=10, env=env
)
print("Return code:", result.returncode)
print("Stdout:", result.stdout)
print("Stderr:", result.stderr)
