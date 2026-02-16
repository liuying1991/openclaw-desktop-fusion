---
name: fusion-desktop
description: 融合桌面控制能力。整合PyAutoGUI和xdotool，跨平台支持Windows/Linux。支持截图、鼠标控制、键盘输入、滚动等操作。超越OpenClaw的computer-use和windows-gui-control。
version: 2.0.0
allowed-tools: Bash, exec
---

# Fusion Desktop - 融合桌面控制

## 功能说明

这是一个超级桌面控制技能，融合了三方优势：

### 来源分析
| 来源 | 能力 | 优势 |
|------|------|------|
| Trae Agent | RunCommand | 命令执行 |
| OpenClaw | computer-use | 17种标准动作 |
| OpenClaw | windows-gui-control | PyAutoGUI实现 |
| 开源 | PyAutoGUI | 成熟稳定 |
| 开源 | xdotool | Linux支持 |

### 融合能力
1. **截图** - 全屏/区域/多显示器
2. **鼠标控制** - 移动/点击/双击/拖拽/滚动
3. **键盘输入** - 英文/中文/快捷键/组合键
4. **智能定位** - 图像识别/坐标计算
5. **跨平台** - Windows/Linux兼容

## 使用方法

### 截图
```json
{"action": "screenshot", "path": "C:/tmp/screen.png"}
{"action": "screenshot", "region": [0, 0, 500, 500], "path": "C:/tmp/region.png"}
```

### 鼠标操作
```json
{"action": "move", "x": 500, "y": 400}
{"action": "click", "x": 500, "y": 400, "button": "left", "clicks": 1}
{"action": "double_click", "x": 500, "y": 400}
{"action": "right_click", "x": 500, "y": 400}
{"action": "drag", "start": [100, 100], "end": [500, 500]}
{"action": "scroll", "direction": "down", "amount": 5}
{"action": "position"}
```

### 键盘操作
```json
{"action": "type", "text": "Hello World"}
{"action": "type", "text": "你好世界"}
{"action": "key", "key": "enter"}
{"action": "hotkey", "keys": ["ctrl", "c"]}
{"action": "hotkey", "keys": ["ctrl", "alt", "delete"]}
```

### 图像识别
```json
{"action": "locate", "image": "C:/tmp/button.png"}
{"action": "locate_and_click", "image": "C:/tmp/button.png", "confidence": 0.9}
```

## 执行脚本

```bash
python C:/tmp/openclaw-desktop-fusion/skills/fusion-desktop/scripts/desktop.py <action> '<json-params>'
```
