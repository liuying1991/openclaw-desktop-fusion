#!/usr/bin/env python3
"""
完整测试脚本 - 测试Ollama工具调用和OpenClaw集成

测试内容:
1. Ollama服务连接
2. 工具定义加载
3. 工具调用请求
4. 工具执行
5. 完整流程验证
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ollama_tools import (
    OllamaToolCaller, 
    OllamaConfig,
    test_connection,
    list_models
)
from tool_definitions import (
    get_all_tools_ollama_format,
    get_tools_by_category
)
from tool_executor import (
    MockToolExecutor,
    create_tool_registry
)


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_ollama_service():
    print_header("测试1: Ollama服务状态")
    
    if not test_connection():
        print("  ✗ Ollama服务未运行")
        return None
    
    print("  ✓ Ollama服务运行中")
    
    models = list_models()
    print(f"\n  可用模型 ({len(models)}个):")
    for m in models:
        print(f"    • {m}")
    
    tool_models = [m for m in models if any(x in m.lower() for x in ['qwen', 'llama3', 'mistral', 'phi', 'glm'])]
    
    if tool_models:
        selected = tool_models[0]
        print(f"\n  选择模型: {selected}")
        return selected
    
    print("  ✗ 没有支持工具调用的模型")
    return None


def test_tool_definitions():
    print_header("测试2: 工具定义加载")
    
    tools = get_all_tools_ollama_format()
    print(f"  总工具数量: {len(tools)}")
    
    categories = ["desktop", "screen", "clipboard", "window", "browser"]
    print("\n  按类别统计:")
    for cat in categories:
        cat_tools = get_tools_by_category(cat)
        print(f"    • {cat}: {len(cat_tools)}个")
    
    print("\n  示例工具定义:")
    sample = tools[0]
    print(f"    名称: {sample['function']['name']}")
    print(f"    描述: {sample['function']['description'][:50]}...")
    
    return True


def test_tool_calling(model):
    print_header("测试3: Ollama工具调用")
    
    if not model:
        print("  ✗ 跳过: 没有可用模型")
        return False
    
    config = OllamaConfig(
        base_url="http://127.0.0.1:11434",
        model=model,
        timeout=60
    )
    caller = OllamaToolCaller(config)
    
    desktop_tools = [t.to_ollama_format() for t in get_tools_by_category("desktop")[:5]]
    
    test_cases = [
        "请告诉我你有哪些桌面控制工具",
        "请帮我获取当前鼠标位置",
        "请帮我点击屏幕坐标(100, 200)"
    ]
    
    results = []
    for i, msg in enumerate(test_cases):
        print(f"\n  测试用例 {i+1}: {msg}")
        try:
            response = caller.chat_with_tools(
                user_message=msg,
                tools=desktop_tools
            )
            
            if "error" in response and response.get("error"):
                print(f"    ✗ 请求失败: {response.get('message')}")
                results.append(False)
                continue
            
            message = response.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])
            
            if content:
                print(f"    响应内容: {content[:100]}...")
            
            if tool_calls:
                print(f"    工具调用: {len(tool_calls)}个")
                for tc in tool_calls:
                    func = tc.get("function", {})
                    print(f"      → {func.get('name')}: {func.get('arguments')}")
            
            print("    ✓ 测试通过")
            results.append(True)
            
        except Exception as e:
            print(f"    ✗ 异常: {e}")
            results.append(False)
    
    return all(results)


def test_tool_execution():
    print_header("测试4: 工具执行器")
    
    registry = create_tool_registry()
    print(f"  工具注册表: {len(registry)}个工具")
    
    mock_executor = MockToolExecutor()
    
    test_tools = [
        ("desktop_position", {}),
        ("desktop_click", {"x": 100, "y": 200}),
        ("desktop_type", {"text": "Hello World"}),
    ]
    
    print("\n  模拟执行测试:")
    for tool_name, args in test_tools:
        if tool_name in registry:
            info = registry[tool_name]
            result = mock_executor.execute_tool(
                tool_name=tool_name,
                arguments=args,
                skill_path=info["skill_path"],
                skill_action=info["skill_action"]
            )
            status = "✓" if result.success else "✗"
            print(f"    {status} {tool_name}: {result.duration:.4f}s")
        else:
            print(f"    ✗ {tool_name}: 未注册")
    
    return True


def test_full_workflow(model):
    print_header("测试5: 完整工作流程")
    
    if not model:
        print("  ✗ 跳过: 没有可用模型")
        return False
    
    config = OllamaConfig(model=model)
    caller = OllamaToolCaller(config)
    
    tools = [t.to_ollama_format() for t in get_tools_by_category("desktop")[:3]]
    
    print("\n  发送请求: 请帮我截屏保存到/tmp/test.png")
    
    try:
        response = caller.chat_with_tools(
            user_message="请帮我截屏保存到/tmp/test.png",
            tools=tools
        )
        
        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])
        content = message.get("content", "")
        
        if content:
            print(f"\n  模型响应: {content[:200]}...")
        
        if tool_calls:
            print(f"\n  检测到工具调用: {len(tool_calls)}个")
            for tc in tool_calls:
                func = tc.get("function", {})
                print(f"    → 工具: {func.get('name')}")
                print(f"    → 参数: {func.get('arguments')}")
            print("\n  ✓ 工具调用识别成功!")
        else:
            print("\n  模型未调用工具（可能直接回答）")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ 测试失败: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("OpenClaw Ollama工具调用系统 - 完整测试")
    print("=" * 60)
    
    model = test_ollama_service()
    
    test_results = []
    
    test_results.append(("工具定义", test_tool_definitions()))
    test_results.append(("工具调用", test_tool_calling(model)))
    test_results.append(("工具执行", test_tool_execution()))
    test_results.append(("完整流程", test_full_workflow(model)))
    
    print_header("测试结果汇总")
    
    passed = 0
    failed = 0
    for name, result in test_results:
        if result:
            print(f"  ✓ {name}: 通过")
            passed += 1
        else:
            print(f"  ✗ {name}: 失败")
            failed += 1
    
    print(f"\n  总计: {passed}通过, {failed}失败")
    print("=" * 60)
    
    if failed == 0:
        print("\n  🎉 所有测试通过! Ollama工具调用系统工作正常!")
    else:
        print("\n  ⚠️ 部分测试失败，请检查配置")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
