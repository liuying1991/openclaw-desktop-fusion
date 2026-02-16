---
name: fusion-window
description: 融合窗口管理能力。窗口查找、激活、移动、调整大小、多显示器支持。超越OpenClaw的窗口管理功能。
version: 2.0.0
allowed-tools: Bash, exec
---

# Fusion Window - 融合窗口管理

## 功能说明

这是一个超级窗口管理技能，融合了三方优势：

### 融合能力
1. **窗口查找** - 按标题/类名查找
2. **窗口激活** - 激活指定窗口
3. **窗口移动** - 移动窗口位置
4. **窗口调整** - 调整窗口大小
5. **多显示器** - 多屏支持
6. **窗口列表** - 获取所有窗口

## 使用方法

### 窗口查找
```json
{"action": "find", "title": "记事本"}
{"action": "list"}
```

### 窗口操作
```json
{"action": "activate", "title": "记事本"}
{"action": "move", "title": "记事本", "x": 0, "y": 0}
{"action": "resize", "title": "记事本", "width": 800, "height": 600}
{"action": "close", "title": "记事本"}
```

### 多显示器
```json
{"action": "monitors"}
```

## 执行脚本

```bash
python C:/tmp/openclaw-desktop-fusion/skills/fusion-window/scripts/window.py <action> '<json-params>'
```
