#!/usr/bin/env python3
import subprocess
import json
import os

env = os.environ.copy()
env['DISPLAY'] = ':0'
env['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'

print("=== Test Browser ===")
result = subprocess.run(
    ['node', '/mnt/c/tmp/openclaw-desktop-fusion/skills/fusion-browser/scripts/browser.js', 'open', '-'],
    input='{"url":"https://example.com","headless":true}',
    capture_output=True, text=True, timeout=60, env=env
)
print("Return code:", result.returncode)
print("Stdout:", result.stdout[:500] if result.stdout else '')
print("Stderr:", result.stderr[:500] if result.stderr else '')

print("\n=== Test Clipboard Copy ===")
result = subprocess.run(
    ['python3', '/mnt/c/tmp/openclaw-desktop-fusion/skills/fusion-clipboard/scripts/clipboard.py', 'copy', '-'],
    input='{"text":"Test clipboard"}',
    capture_output=True, text=True, timeout=10, env=env
)
print("Return code:", result.returncode)
print("Stdout:", result.stdout)
print("Stderr:", result.stderr)
