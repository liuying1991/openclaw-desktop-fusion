"""
test_ollama_tools.py - Ollama工具调用测试脚本

测试fusion-ollama-tools模块的各个组件。

作者: AI Assistant
版本: 1.0.0
日期: 2026-02-17
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_definitions import (
    ALL_TOOLS,
    get_tool_by_name,
    get_all_tools_ollama_format,
    get_tools_by_category,
    print_tools_info
)
from tool_executor import (
    ToolExecutor,
    MockToolExecutor,
    ExecutionResult,
    create_tool_registry
)


def test_tool_definitions():
    """
    测试工具定义模块
    """
    print("\n" + "=" * 60)
    print("测试1: 工具定义模块")
    print("=" * 60)
    
    print(f"\n总工具数量: {len(ALL_TOOLS)}")
    
    print("\n按类别统计:")
    categories = ["desktop", "screen", "clipboard", "window", "browser"]
    for cat in categories:
        tools = get_tools_by_category(cat)
        print(f"  • {cat}: {len(tools)}个工具")
    
    print("\n测试工具查找:")
    tool = get_tool_by_name("desktop_click")
    if tool:
        print(f"  ✓ 找到工具: {tool.name}")
        print(f"    描述: {tool.description}")
        print(f"    参数数量: {len(tool.parameters)}")
    else:
        print("  ✗ 未找到工具")
    
    print("\n测试Ollama格式转换:")
    ollama_tools = get_all_tools_ollama_format()
    print(f"  转换后工具数量: {len(ollama_tools)}")
    
    sample = ollama_tools[0]
    print(f"  示例工具: {sample['function']['name']}")
    
    return True


def test_tool_executor():
    """
    测试工具执行器模块
    """
    print("\n" + "=" * 60)
    print("测试2: 工具执行器模块")
    print("=" * 60)
    
    print("\n创建工具注册表:")
    registry = create_tool_registry()
    print(f"  注册工具数量: {len(registry)}")
    
    print("\n测试模拟执行器:")
    mock_executor = MockToolExecutor()
    
    result = mock_executor.execute_tool(
        tool_name="desktop_click",
        arguments={"x": 100, "y": 200},
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="click"
    )
    
    print(f"  工具名称: {result.tool_name}")
    print(f"  执行成功: {result.success}")
    print(f"  执行耗时: {result.duration:.4f}秒")
    print(f"  结果: {json.dumps(result.result, ensure_ascii=False)}")
    
    print("\n测试批量执行:")
    tool_calls = [
        {"function": {"name": "desktop_move", "arguments": {"x": 500, "y": 300}}},
        {"function": {"name": "desktop_click", "arguments": {"x": 500, "y": 300}}},
    ]
    
    results = mock_executor.execute_tool_calls(tool_calls, registry)
    print(f"  执行结果数量: {len(results)}")
    for r in results:
        print(f"    • {r.tool_name}: {'成功' if r.success else '失败'}")
    
    return True


def test_ollama_tools_module():
    """
    测试Ollama工具调用核心模块
    """
    print("\n" + "=" * 60)
    print("测试3: Ollama工具调用核心模块")
    print("=" * 60)
    
    from ollama_tools import (
        OllamaToolCaller,
        OllamaConfig,
        test_connection,
        list_models
    )
    
    print("\n测试Ollama连接:")
    if test_connection():
        print("  ✓ Ollama连接成功")
        
        print("\n可用模型:")
        models = list_models()
        for model in models[:5]:
            print(f"    • {model}")
        if len(models) > 5:
            print(f"    ... 共{len(models)}个模型")
    else:
        print("  ✗ Ollama连接失败（请确保Ollama服务正在运行）")
    
    print("\n创建工具调用器:")
    config = OllamaConfig(
        base_url="http://127.0.0.1:11434",
        model="qwen3:latest"
    )
    caller = OllamaToolCaller(config)
    
    print(f"  配置: {config.base_url}, 模型: {config.model}")
    print(f"  可用工具: {len(caller.get_available_tools())}个")
    
    return True


def test_tool_call_simulation():
    """
    模拟完整的工具调用流程
    """
    print("\n" + "=" * 60)
    print("测试4: 工具调用流程模拟")
    print("=" * 60)
    
    from ollama_tools import OllamaToolCaller, OllamaConfig
    
    config = OllamaConfig(model="qwen3:latest")
    caller = OllamaToolCaller(config)
    
    print("\n模拟工具调用响应:")
    mock_response = {
        "model": "qwen3:latest",
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "desktop_position",
                        "arguments": {}
                    }
                },
                {
                    "function": {
                        "name": "desktop_click",
                        "arguments": {"x": 100, "y": 200, "button": "left"}
                    }
                }
            ]
        }
    }
    
    print("  模拟响应包含2个工具调用:")
    for tc in mock_response["message"]["tool_calls"]:
        print(f"    • {tc['function']['name']}: {tc['function']['arguments']}")
    
    print("\n处理工具调用:")
    results = caller.process_tool_calls(mock_response)
    
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"  {status} {result.tool_name}")
        if result.error:
            print(f"      错误: {result.error}")
    
    return True


def run_all_tests():
    """
    运行所有测试
    """
    print("=" * 60)
    print("OpenClaw Ollama工具调用模块测试")
    print("=" * 60)
    
    tests = [
        ("工具定义模块", test_tool_definitions),
        ("工具执行器模块", test_tool_executor),
        ("Ollama核心模块", test_ollama_tools_module),
        ("工具调用流程", test_tool_call_simulation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, success, error in results:
        if success:
            print(f"  ✓ {name}: 通过")
            passed += 1
        else:
            print(f"  ✗ {name}: 失败")
            if error:
                print(f"      错误: {error}")
            failed += 1
    
    print(f"\n总计: {passed}通过, {failed}失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
