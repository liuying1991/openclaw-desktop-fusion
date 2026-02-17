---
name: fusion-ollama-tools
description: Ollama原生工具调用支持模块。将OpenClaw桌面控制技能转换为Ollama工具调用格式，支持Ollama原生API和LangChain两种调用方式。解决OpenClaw对Ollama工具调用支持不完整的问题。
version: 1.0.0
allowed-tools: Bash, exec
dependencies:
  - requests>=2.28.0
  - langchain-experimental>=0.3.0 (可选)
  - langchain-ollama>=0.2.0 (可选)
---

# Fusion Ollama Tools - Ollama工具调用支持

## 功能说明

这是一个专门为OpenClaw系统设计的Ollama工具调用支持模块，解决了OpenClaw使用`openai-completions` API类型导致工具调用不支持的问题。

### 核心功能

1. **工具定义转换** - 将桌面控制技能转换为Ollama原生工具调用格式
2. **工具执行器** - 执行工具调用并返回结果
3. **双模式支持** - 支持Ollama原生API和LangChain两种调用方式
4. **完整工具集** - 包含桌面控制、屏幕操作、剪贴板、窗口管理、浏览器等工具

### 支持的工具类别

| 类别 | 工具数量 | 说明 |
|------|---------|------|
| 桌面控制 | 13个 | 截图、鼠标、键盘、图像识别 |
| 屏幕操作 | 3个 | 截图Base64、OCR、屏幕尺寸 |
| 剪贴板 | 4个 | 复制、粘贴、获取、清空 |
| 窗口管理 | 6个 | 列表、查找、激活、关闭、最小化、最大化 |
| 浏览器 | 3个 | 打开、截图、关闭 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Agent                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              fusion-ollama-tools                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           OllamaToolCaller / LangChainToolCaller    │   │
│  │  - 工具定义转换                                      │   │
│  │  - 工具调用处理                                      │   │
│  │  - 结果格式化                                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Ollama API                                │
│              http://127.0.0.1:11434/api/chat                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 桌面控制技能层                                │
│  fusion-desktop | fusion-screen | fusion-browser | ...     │
└─────────────────────────────────────────────────────────────┘
```

## 使用方法

### 方式一：Ollama原生API调用

```python
from ollama_tools import OllamaToolCaller, OllamaConfig

# 创建配置
config = OllamaConfig(
    base_url="http://127.0.0.1:11434",
    model="qwen3:latest"
)

# 创建调用器
caller = OllamaToolCaller(config)

# 发送带工具的聊天请求
response = caller.chat_with_tools(
    user_message="请帮我截个屏保存到/tmp/test.png",
    system_prompt="你是一个桌面控制助手"
)

# 处理工具调用
if "message" in response:
    tool_calls = response["message"].get("tool_calls", [])
    if tool_calls:
        results = caller.process_tool_calls(response)
        for result in results:
            print(f"工具: {result.tool_name}")
            print(f"结果: {result.result}")
```

### 方式二：完整对话流程（自动执行工具）

```python
from ollama_tools import OllamaToolCaller

caller = OllamaToolCaller()

# 自动执行工具并返回最终结果
final_response = caller.chat_with_tool_execution(
    user_message="请帮我点击屏幕坐标(500, 300)",
    max_iterations=5
)

print(final_response)
```

### 方式三：使用LangChain（可选）

```python
from ollama_tools import LangChainToolCaller, OllamaConfig

config = OllamaConfig(model="qwen3:latest")
caller = LangChainToolCaller(config)

response = caller.chat_with_tools(
    user_message="获取当前鼠标位置"
)
print(response)
```

## 工具定义示例

### Ollama原生格式

```json
{
  "type": "function",
  "function": {
    "name": "desktop_click",
    "description": "在指定位置执行鼠标点击操作",
    "parameters": {
      "type": "object",
      "properties": {
        "x": {"type": "integer", "description": "点击位置X坐标"},
        "y": {"type": "integer", "description": "点击位置Y坐标"},
        "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"}
      },
      "required": ["x", "y"]
    }
  }
}
```

## 命令行使用

### 查看工具列表

```bash
python skills/fusion-ollama-tools/scripts/tool_definitions.py
```

### 测试Ollama连接

```bash
python skills/fusion-ollama-tools/scripts/ollama_tools.py
```

### 测试工具执行器

```bash
python skills/fusion-ollama-tools/scripts/tool_executor.py
```

## 依赖安装

### 基础依赖

```bash
pip install requests
```

### LangChain支持（可选）

```bash
pip install langchain-experimental langchain-ollama
```

## 支持的模型

需要使用支持工具调用的Ollama模型：

- **推荐**: qwen3, qwen2.5
- **支持**: llama3.1, llama3.2, llama3.3
- **支持**: mistral, mistral-nemo
- **支持**: phi-3
- **支持**: glm-4

## 与OpenClaw集成

### 配置修改

在OpenClaw的配置中，可以添加此技能作为工具调用适配层：

```json
{
  "plugins": {
    "entries": {
      "ollama-tools": {
        "enabled": true
      }
    }
  }
}
```

### 调用流程

1. OpenClaw Agent接收用户消息
2. 通过fusion-ollama-tools将消息发送到Ollama
3. Ollama识别需要调用的工具
4. fusion-ollama-tools执行对应的技能脚本
5. 将结果返回给Ollama生成最终响应

## 注意事项

1. **模型要求**: 确保使用的模型支持工具调用功能
2. **Ollama版本**: 建议使用Ollama >= 0.3.0
3. **技能路径**: 确保技能脚本路径正确
4. **权限**: 某些操作可能需要管理员权限

## 文件结构

```
skills/fusion-ollama-tools/
├── SKILL.md                    # 本文档
├── scripts/
│   ├── ollama_tools.py        # 核心模块
│   ├── tool_definitions.py    # 工具定义
│   └── tool_executor.py       # 工具执行器
└── requirements.txt           # 依赖列表
```

## 更新日志

### v1.0.0 (2026-02-17)
- 初始版本
- 支持Ollama原生API工具调用
- 支持LangChain工具调用（可选）
- 包含29个桌面控制工具定义
