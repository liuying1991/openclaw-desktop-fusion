# OpenClaw Ollama工具调用支持升级方案

## 一、问题分析

### 1.1 当前问题
OpenClaw系统当前使用`openai-completions` API类型连接Ollama，这导致：
- 工具调用(Tool Calling)功能不被支持
- 无法利用Ollama原生工具调用能力
- 模型无法自动识别和调用技能工具

### 1.2 根本原因
```json
"providers": {
  "ollama": {
    "baseUrl": "http://127.0.0.1:11434/v1",
    "api": "openai-completions",  // 问题所在：使用OpenAI兼容API
    ...
  }
}
```

### 1.3 Ollama原生工具调用支持
Ollama从v0.3.0开始原生支持工具调用，支持的模型包括：
- Llama 3.1/3.2/3.3
- Qwen2.5/Qwen3
- Mistral
- Phi-3
- GLM-4

## 二、技术方案

### 2.1 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| A. 修改OpenClaw核心配置 | 最彻底 | 需要修改OpenClaw源码 | ⭐⭐⭐ |
| B. 创建中间适配器层 | 不修改核心 | 增加复杂度 | ⭐⭐⭐⭐ |
| C. LangChain技能模块 | 成熟稳定 | 需要Python依赖 | ⭐⭐⭐⭐⭐ |

### 2.2 推荐方案：LangChain + OllamaFunctions技能模块

基于现有的`openclaw-skills-fusion`项目，创建一个专门的Ollama工具调用适配技能。

## 三、实现计划

### 阶段1：创建Ollama工具调用核心模块
- 创建`fusion-ollama-tools`技能
- 实现Ollama原生API工具调用
- 支持多工具绑定和执行

### 阶段2：集成OpenClaw技能系统
- 将桌面控制技能转换为工具定义
- 实现工具调用到技能执行的映射
- 添加工具调用结果处理

### 阶段3：测试验证
- 单元测试
- 集成测试
- 端到端测试

## 四、技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Agent                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              fusion-ollama-tools (新技能)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           LangChain + OllamaFunctions               │   │
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
│              (原生工具调用支持)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 桌面控制技能层                                │
│  fusion-desktop | fusion-screen | fusion-browser | ...     │
└─────────────────────────────────────────────────────────────┘
```

## 五、核心代码设计

### 5.1 工具定义格式（Ollama原生）
```json
{
  "type": "function",
  "function": {
    "name": "desktop_click",
    "description": "在指定位置执行鼠标点击",
    "parameters": {
      "type": "object",
      "properties": {
        "x": {"type": "integer", "description": "X坐标"},
        "y": {"type": "integer", "description": "Y坐标"},
        "button": {"type": "string", "enum": ["left", "right", "middle"]}
      },
      "required": ["x", "y"]
    }
  }
}
```

### 5.2 工具调用响应格式
```json
{
  "tool_calls": [{
    "function": {
      "name": "desktop_click",
      "arguments": {"x": 100, "y": 200, "button": "left"}
    }
  }]
}
```

## 六、依赖要求

### 6.1 Python依赖
```
langchain>=0.3.0
langchain-ollama>=0.2.0
langchain-experimental>=0.3.0
ollama>=0.4.0
pydantic>=2.0.0
```

### 6.2 系统要求
- Ollama >= 0.3.0
- Python >= 3.10
- 支持工具调用的模型（如qwen3, llama3.1等）

## 七、实施步骤

### Step 1: 创建技能目录结构
```
skills/fusion-ollama-tools/
├── SKILL.md
├── scripts/
│   ├── ollama_tools.py      # 核心工具调用模块
│   ├── tool_definitions.py  # 工具定义
│   └── tool_executor.py     # 工具执行器
└── requirements.txt
```

### Step 2: 实现核心模块
1. `ollama_tools.py` - Ollama原生API工具调用
2. `tool_definitions.py` - 桌面控制工具定义
3. `tool_executor.py` - 工具执行和结果处理

### Step 3: 测试验证
1. 单个工具调用测试
2. 多工具协同测试
3. 错误处理测试

## 八、预期效果

### 8.1 功能提升
- ✅ 完全支持Ollama原生工具调用
- ✅ 自动识别和执行技能工具
- ✅ 支持多工具协同工作
- ✅ 流式响应支持

### 8.2 性能优化
- 减少Token消耗（工具定义按需加载）
- 提高响应速度（原生API调用）
- 增强稳定性（成熟的LangChain框架）

## 九、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 模型不支持工具调用 | 中 | 检测模型能力，提供降级方案 |
| Python依赖冲突 | 低 | 使用虚拟环境隔离 |
| API格式变化 | 低 | 使用稳定的LangChain封装 |

## 十、时间规划

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 1 | 创建核心模块 | 1天 |
| 2 | 集成技能系统 | 1天 |
| 3 | 测试验证 | 0.5天 |
| 4 | 文档完善 | 0.5天 |

**总计：3天**

---

*文档版本：1.0*
*创建日期：2026-02-17*
*作者：AI Assistant*
