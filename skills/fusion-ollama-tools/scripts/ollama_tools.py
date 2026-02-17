"""
ollama_tools.py - Ollama工具调用核心模块

实现Ollama原生API的工具调用支持，包括：
1. 直接使用Ollama原生API进行工具调用
2. 使用LangChain OllamaFunctions进行工具调用（可选）
3. 工具调用结果处理和执行

作者: AI Assistant
版本: 1.0.0
日期: 2026-02-17
"""

import json
import requests
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
import os
import sys

try:
    from langchain_experimental.llms.ollama_functions import OllamaFunctions
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from tool_definitions import (
    ALL_TOOLS, 
    get_tool_by_name, 
    get_all_tools_ollama_format,
    ToolDefinition
)
from tool_executor import (
    ToolExecutor, 
    ExecutionResult,
    create_tool_registry
)


@dataclass
class OllamaConfig:
    """
    Ollama配置
    
    Attributes:
        base_url: Ollama API基础URL
        model: 模型名称
        timeout: 请求超时时间
        stream: 是否使用流式响应
    """
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3:latest"
    timeout: int = 120
    stream: bool = False


class OllamaToolCaller:
    """
    Ollama原生API工具调用器
    
    直接使用Ollama原生API进行工具调用，无需LangChain依赖。
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        初始化工具调用器
        
        Args:
            config: Ollama配置，为None时使用默认配置
        """
        self.config = config or OllamaConfig()
        self.tool_registry = create_tool_registry()
        self.executor = ToolExecutor()
    
    def _build_chat_request(
        self, 
        messages: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        构建聊天请求体
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            
        Returns:
            Dict: 请求体
        """
        return {
            "model": self.config.model,
            "messages": messages,
            "stream": self.config.stream,
            "tools": tools
        }
    
    def chat_with_tools(
        self, 
        user_message: str, 
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送带工具的聊天请求
        
        Args:
            user_message: 用户消息
            tools: 工具定义列表，为None时使用所有工具
            system_prompt: 系统提示词
            
        Returns:
            Dict: 响应结果
        """
        if tools is None:
            tools = get_all_tools_ollama_format()
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        request_body = self._build_chat_request(messages, tools)
        
        try:
            response = requests.post(
                f"{self.config.base_url}/api/chat",
                json=request_body,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": f"Request failed: {str(e)}"
            }
    
    def process_tool_calls(
        self, 
        response: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """
        处理工具调用响应
        
        Args:
            response: Ollama API响应
            
        Returns:
            List[ExecutionResult]: 执行结果列表
        """
        results = []
        
        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            tool_name = func.get("name", "")
            arguments = func.get("arguments", {})
            
            if tool_name in self.tool_registry:
                tool_info = self.tool_registry[tool_name]
                result = self.executor.execute_tool(
                    tool_name=tool_name,
                    arguments=arguments,
                    skill_path=tool_info["skill_path"],
                    skill_action=tool_info["skill_action"]
                )
            else:
                result = ExecutionResult(
                    success=False,
                    tool_name=tool_name,
                    result={},
                    error=f"Unknown tool: {tool_name}"
                )
            
            results.append(result)
        
        return results
    
    def chat_with_tool_execution(
        self, 
        user_message: str, 
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        带工具执行的完整对话流程
        
        Args:
            user_message: 用户消息
            tools: 工具定义列表
            system_prompt: 系统提示词
            max_iterations: 最大迭代次数
            
        Returns:
            Dict: 最终响应
        """
        if tools is None:
            tools = get_all_tools_ollama_format()
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        iteration = 0
        final_response = None
        
        while iteration < max_iterations:
            iteration += 1
            
            request_body = self._build_chat_request(messages, tools)
            
            try:
                response = requests.post(
                    f"{self.config.base_url}/api/chat",
                    json=request_body,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                response_data = response.json()
                
            except requests.exceptions.RequestException as e:
                return {
                    "error": True,
                    "message": f"Request failed: {str(e)}",
                    "iteration": iteration
                }
            
            message = response_data.get("message", {})
            tool_calls = message.get("tool_calls", [])
            content = message.get("content", "")
            
            messages.append(message)
            
            if not tool_calls:
                final_response = response_data
                break
            
            for tool_call in tool_calls:
                func = tool_call.get("function", {})
                tool_name = func.get("name", "")
                arguments = func.get("arguments", {})
                
                if tool_name in self.tool_registry:
                    tool_info = self.tool_registry[tool_name]
                    result = self.executor.execute_tool(
                        tool_name=tool_name,
                        arguments=arguments,
                        skill_path=tool_info["skill_path"],
                        skill_action=tool_info["skill_action"]
                    )
                    
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result.result, ensure_ascii=False),
                        "name": tool_name
                    })
                else:
                    messages.append({
                        "role": "tool",
                        "content": json.dumps({"error": f"Unknown tool: {tool_name}"}),
                        "name": tool_name
                    })
        
        if final_response is None:
            final_response = {
                "error": True,
                "message": "Max iterations reached",
                "iteration": iteration
            }
        
        return final_response
    
    def get_available_tools(self) -> List[str]:
        """
        获取可用工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return list(self.tool_registry.keys())


class LangChainToolCaller:
    """
    基于LangChain的工具调用器
    
    使用LangChain的OllamaFunctions进行工具调用。
    需要安装langchain-experimental包。
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        初始化LangChain工具调用器
        
        Args:
            config: Ollama配置
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain not available. Install with: "
                "pip install langchain-experimental langchain-ollama"
            )
        
        self.config = config or OllamaConfig()
        self.tool_registry = create_tool_registry()
        self.executor = ToolExecutor()
        
        self.llm = OllamaFunctions(
            model=self.config.model,
            base_url=self.config.base_url,
            format="json"
        )
    
    def bind_tools(self, tools: Optional[List[Dict[str, Any]]] = None):
        """
        绑定工具到模型
        
        Args:
            tools: 工具定义列表
            
        Returns:
            绑定工具后的模型
        """
        if tools is None:
            tools = get_all_tools_ollama_format()
        
        return self.llm.bind_tools(tools)
    
    def chat_with_tools(
        self, 
        user_message: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        使用LangChain进行工具调用
        
        Args:
            user_message: 用户消息
            tools: 工具定义列表
            
        Returns:
            Dict: 响应结果
        """
        llm_with_tools = self.bind_tools(tools)
        
        try:
            response = llm_with_tools.invoke(user_message)
            
            if hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
                func_call = response.additional_kwargs['function_call']
                tool_name = func_call.get('name', '')
                arguments = json.loads(func_call.get('arguments', '{}'))
                
                if tool_name in self.tool_registry:
                    tool_info = self.tool_registry[tool_name]
                    result = self.executor.execute_tool(
                        tool_name=tool_name,
                        arguments=arguments,
                        skill_path=tool_info["skill_path"],
                        skill_action=tool_info["skill_action"]
                    )
                    return {
                        "tool_called": tool_name,
                        "arguments": arguments,
                        "result": result.to_dict()
                    }
            
            return {
                "content": response.content if hasattr(response, 'content') else str(response),
                "tool_called": None
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e)
            }


def create_tool_caller(
    use_langchain: bool = False,
    config: Optional[OllamaConfig] = None
) -> Union[OllamaToolCaller, LangChainToolCaller]:
    """
    创建工具调用器工厂函数
    
    Args:
        use_langchain: 是否使用LangChain
        config: Ollama配置
        
    Returns:
        工具调用器实例
    """
    if use_langchain:
        if not LANGCHAIN_AVAILABLE:
            print("Warning: LangChain not available, falling back to native API")
            return OllamaToolCaller(config)
        return LangChainToolCaller(config)
    return OllamaToolCaller(config)


def test_connection(base_url: str = "http://127.0.0.1:11434") -> bool:
    """
    测试Ollama连接
    
    Args:
        base_url: Ollama API地址
        
    Returns:
        bool: 连接是否成功
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def list_models(base_url: str = "http://127.0.0.1:11434") -> List[str]:
    """
    列出可用的Ollama模型
    
    Args:
        base_url: Ollama API地址
        
    Returns:
        List[str]: 模型名称列表
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except:
        pass
    return []


if __name__ == "__main__":
    print("=" * 60)
    print("Ollama工具调用核心模块测试")
    print("=" * 60)
    
    print("\n1. 测试Ollama连接...")
    if test_connection():
        print("   ✓ Ollama连接成功")
        
        print("\n2. 列出可用模型:")
        models = list_models()
        for model in models:
            print(f"   • {model}")
    else:
        print("   ✗ Ollama连接失败，请确保Ollama服务正在运行")
    
    print("\n3. 创建工具调用器...")
    caller = OllamaToolCaller()
    
    print(f"   可用工具数量: {len(caller.get_available_tools())}")
    print("   工具列表:")
    for tool_name in caller.get_available_tools()[:5]:
        print(f"     • {tool_name}")
    print("     ...")
    
    print("\n4. 工具定义示例:")
    tools = get_all_tools_ollama_format()[:1]
    print(json.dumps(tools[0], indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
