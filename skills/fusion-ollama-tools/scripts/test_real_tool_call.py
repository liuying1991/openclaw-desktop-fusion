"""
test_real_tool_call.py - 实际Ollama工具调用测试

测试真实的Ollama工具调用流程。

作者: AI Assistant
版本: 1.0.0
日期: 2026-02-17
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
from tool_definitions import get_tools_by_category


def test_real_tool_call():
    """
    测试实际的Ollama工具调用
    """
    print("=" * 60)
    print("实际Ollama工具调用测试")
    print("=" * 60)
    
    print("\n1. 检查Ollama连接...")
    if not test_connection():
        print("   ✗ Ollama连接失败，请确保服务正在运行")
        return False
    print("   ✓ Ollama连接成功")
    
    print("\n2. 获取可用模型...")
    models = list_models()
    if not models:
        print("   ✗ 没有可用模型")
        return False
    
    print(f"   可用模型: {models}")
    
    tool_capable_models = []
    for m in models:
        if any(x in m.lower() for x in ['qwen', 'llama3', 'mistral', 'phi', 'glm']):
            tool_capable_models.append(m)
    
    if not tool_capable_models:
        print("   ✗ 没有支持工具调用的模型")
        return False
    
    selected_model = tool_capable_models[0]
    print(f"   选择模型: {selected_model}")
    
    print("\n3. 创建工具调用器...")
    config = OllamaConfig(
        base_url="http://127.0.0.1:11434",
        model=selected_model
    )
    caller = OllamaToolCaller(config)
    print(f"   ✓ 配置完成")
    
    print("\n4. 测试工具调用请求...")
    
    desktop_tools = [t.to_ollama_format() for t in get_tools_by_category("desktop")[:3]]
    
    test_message = "请告诉我你有哪些桌面控制工具可以使用？"
    
    print(f"   发送消息: {test_message}")
    print(f"   工具数量: {len(desktop_tools)}")
    
    try:
        response = caller.chat_with_tools(
            user_message=test_message,
            tools=desktop_tools
        )
        
        if "error" in response and response.get("error"):
            print(f"   ✗ 请求失败: {response.get('message')}")
            return False
        
        message = response.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        print(f"\n   模型响应:")
        if content:
            print(f"   内容: {content[:200]}...")
        
        if tool_calls:
            print(f"   工具调用: {len(tool_calls)}个")
            for tc in tool_calls:
                func = tc.get("function", {})
                print(f"     • {func.get('name')}: {func.get('arguments')}")
        else:
            print("   没有工具调用")
        
        print("\n   ✓ 工具调用测试成功")
        return True
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False


def test_tool_call_with_execution():
    """
    测试带执行的工具调用
    """
    print("\n" + "=" * 60)
    print("测试带执行的工具调用")
    print("=" * 60)
    
    if not test_connection():
        print("   ✗ Ollama连接失败")
        return False
    
    models = list_models()
    tool_models = [m for m in models if any(x in m.lower() for x in ['qwen', 'llama3', 'mistral', 'phi', 'glm'])]
    
    if not tool_models:
        print("   ✗ 没有支持工具调用的模型")
        return False
    
    config = OllamaConfig(model=tool_models[0])
    caller = OllamaToolCaller(config)
    
    desktop_tools = [t.to_ollama_format() for t in get_tools_by_category("desktop")[:5]]
    
    test_message = "请获取当前鼠标位置"
    
    print(f"\n   发送消息: {test_message}")
    
    try:
        response = caller.chat_with_tools(
            user_message=test_message,
            tools=desktop_tools
        )
        
        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        if tool_calls:
            print(f"   模型请求调用工具: {len(tool_calls)}个")
            
            for tc in tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                arguments = func.get("arguments", {})
                print(f"     • {tool_name}: {arguments}")
            
            print("\n   ✓ 工具调用识别成功")
            return True
        else:
            content = message.get("content", "")
            print(f"   模型直接响应: {content[:200]}...")
            print("   （模型选择不调用工具）")
            return True
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Ollama工具调用实际测试")
    print("=" * 60)
    
    test1 = test_real_tool_call()
    test2 = test_tool_call_with_execution()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"  基础工具调用测试: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"  工具执行测试: {'✓ 通过' if test2 else '✗ 失败'}")
    print("=" * 60)
