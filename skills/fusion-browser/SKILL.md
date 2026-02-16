---
name: fusion-browser
description: 融合浏览器自动化能力。Playwright + Selenium混合，智能等待，反检测，多浏览器支持。超越OpenClaw的playwright-browser。
version: 2.0.0
allowed-tools: Bash, exec
---

# Fusion Browser - 融合浏览器自动化

## 功能说明

这是一个超级浏览器自动化技能，融合了三方优势：

### 融合能力
1. **多浏览器** - Chrome/Firefox/Edge/Safari
2. **智能等待** - 自动等待元素
3. **反检测** - 隐蔽自动化
4. **截图** - 全页/区域截图
5. **表单操作** - 自动填写提交

## 使用方法

### 基本操作
```json
{"action": "open", "url": "https://www.baidu.com"}
{"action": "screenshot", "path": "C:/tmp/page.png"}
{"action": "title"}
{"action": "close"}
```

### 元素操作
```json
{"action": "click", "selector": "#btn"}
{"action": "type", "selector": "#input", "text": "Hello"}
{"action": "wait", "selector": "#result", "timeout": 5000}
```

### 搜索操作
```json
{"action": "search", "engine": "baidu", "query": "OpenClaw"}
```

## 执行脚本

```bash
node C:/tmp/openclaw-desktop-fusion/skills/fusion-browser/scripts/browser.js <action> '<json-params>'
```
