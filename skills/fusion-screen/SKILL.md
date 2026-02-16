---
name: fusion-screen
description: 融合屏幕理解能力。OCR文字识别、图像模板匹配、UI元素检测、自动坐标计算。超越OpenClaw的screen-understanding。
version: 2.0.0
allowed-tools: Bash, exec
---

# Fusion Screen - 融合屏幕理解

## 功能说明

这是一个超级屏幕理解技能，融合了三方优势：

### 融合能力
1. **OCR识别** - 多语言文字识别
2. **模板匹配** - 图像查找定位
3. **UI检测** - 按钮/输入框检测
4. **坐标计算** - 智能坐标定位
5. **多显示器** - 多屏支持

## 使用方法

### OCR识别
```json
{"action": "ocr", "region": [0, 0, 500, 500]}
{"action": "ocr_all"}
```

### 模板匹配
```json
{"action": "find_image", "template": "C:/tmp/button.png", "confidence": 0.9}
{"action": "find_all", "template": "C:/tmp/icon.png"}
```

### 屏幕分析
```json
{"action": "analyze"}
{"action": "detect_buttons"}
{"action": "detect_text_fields"}
```

## 执行脚本

```bash
python C:/tmp/openclaw-desktop-fusion/skills/fusion-screen/scripts/screen.py <action> '<json-params>'
```
