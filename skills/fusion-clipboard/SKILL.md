---
name: fusion-clipboard
description: 融合剪贴板能力。跨平台剪贴板操作，支持文本、图片、文件。超越OpenClaw的剪贴板功能。
version: 2.0.0
allowed-tools: Bash, exec
---

# Fusion Clipboard - 融合剪贴板

## 功能说明

这是一个超级剪贴板技能，融合了三方优势：

### 融合能力
1. **文本剪贴板** - 复制/粘贴文本
2. **图片剪贴板** - 复制/粘贴图片
3. **文件剪贴板** - 复制/粘贴文件
4. **历史记录** - 剪贴板历史
5. **跨平台** - Windows/Linux兼容

## 使用方法

### 文本操作
```json
{"action": "copy", "text": "Hello World"}
{"action": "paste"}
{"action": "get"}
```

### 图片操作
```json
{"action": "copy_image", "path": "C:/tmp/image.png"}
{"action": "paste_image", "path": "C:/tmp/pasted.png"}
```

## 执行脚本

```bash
python C:/tmp/openclaw-desktop-fusion/skills/fusion-clipboard/scripts/clipboard.py <action> '<json-params>'
```
