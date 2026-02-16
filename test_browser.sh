#!/bin/bash
export DISPLAY=:0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir

cd /mnt/c/tmp/openclaw-desktop-fusion/skills/fusion-browser/scripts
node browser.js open '{"url":"https://example.com","headless":true}'
