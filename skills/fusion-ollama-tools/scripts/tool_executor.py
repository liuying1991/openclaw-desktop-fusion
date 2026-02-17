"""
tool_executor.py - 工具执行器模块

负责执行Ollama工具调用，将工具调用映射到实际的技能脚本执行。

作者: AI Assistant
版本: 1.0.0
日期: 2026-02-17
"""

import subprocess
import json
import os
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time


@dataclass
class ExecutionResult:
    """
    工具执行结果
    
    Attributes:
        success: 是否成功
        tool_name: 工具名称
        result: 执行结果数据
        error: 错误信息
        duration: 执行耗时(秒)
    """
    success: bool
    tool_name: str
    result: Dict[str, Any]
    error: Optional[str] = None
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict: 结果字典
        """
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "result": self.result,
            "error": self.error,
            "duration": self.duration
        }
    
    def to_ollama_tool_response(self) -> Dict[str, Any]:
        """
        转换为Ollama工具响应格式
        
        Returns:
            Dict: Ollama工具响应格式
        """
        return {
            "role": "tool",
            "content": json.dumps(self.result, ensure_ascii=False),
            "name": self.tool_name
        }


class ToolExecutor:
    """
    工具执行器类
    
    负责将Ollama工具调用转换为实际的技能脚本执行。
    """
    
    def __init__(self, base_path: str = ""):
        """
        初始化工具执行器
        
        Args:
            base_path: 技能脚本的基础路径前缀
        """
        self.base_path = base_path
        self._skill_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_skill_script_path(self, skill_path: str) -> str:
        """
        获取技能脚本的完整路径
        
        Args:
            skill_path: 相对技能路径
            
        Returns:
            str: 完整路径
        """
        if self.base_path:
            return os.path.join(self.base_path, skill_path)
        return skill_path
    
    def _execute_python_skill(
        self, 
        script_path: str, 
        action: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行Python技能脚本
        
        Args:
            script_path: 脚本路径
            action: 动作名称
            params: 参数字典
            
        Returns:
            Dict: 执行结果
        """
        full_path = self._get_skill_script_path(script_path)
        params_json = json.dumps(params, ensure_ascii=False)
        
        try:
            result = subprocess.run(
                ["python", full_path, action, params_json],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": result.stderr or f"Exit code: {result.returncode}"
                }
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Execution timeout (60s)"}
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"JSON parse error: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_node_skill(
        self, 
        script_path: str, 
        action: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行Node.js技能脚本
        
        Args:
            script_path: 脚本路径
            action: 动作名称
            params: 参数字典
            
        Returns:
            Dict: 执行结果
        """
        full_path = self._get_skill_script_path(script_path)
        params_json = json.dumps(params, ensure_ascii=False)
        
        try:
            result = subprocess.run(
                ["node", full_path, action, params_json],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": result.stderr or f"Exit code: {result.returncode}"
                }
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Execution timeout (60s)"}
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"JSON parse error: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        skill_path: str,
        skill_action: str
    ) -> ExecutionResult:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            skill_path: 技能脚本路径
            skill_action: 技能动作名称
            
        Returns:
            ExecutionResult: 执行结果
        """
        start_time = time.time()
        
        try:
            if skill_path.endswith('.py'):
                result = self._execute_python_skill(skill_path, skill_action, arguments)
            elif skill_path.endswith('.js'):
                result = self._execute_node_skill(skill_path, skill_action, arguments)
            else:
                result = {"status": "error", "message": f"Unknown script type: {skill_path}"}
            
            success = result.get("status") == "success"
            duration = time.time() - start_time
            
            return ExecutionResult(
                success=success,
                tool_name=tool_name,
                result=result,
                error=None if success else result.get("message"),
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                tool_name=tool_name,
                result={},
                error=str(e),
                duration=duration
            )
    
    def execute_tool_calls(
        self, 
        tool_calls: List[Dict[str, Any]],
        tool_registry: Dict[str, Dict[str, Any]]
    ) -> List[ExecutionResult]:
        """
        批量执行工具调用
        
        Args:
            tool_calls: Ollama返回的工具调用列表
            tool_registry: 工具注册表 {tool_name: {skill_path, skill_action}}
            
        Returns:
            List[ExecutionResult]: 执行结果列表
        """
        results = []
        
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            tool_name = func.get("name", "")
            arguments = func.get("arguments", {})
            
            if tool_name in tool_registry:
                tool_info = tool_registry[tool_name]
                result = self.execute_tool(
                    tool_name=tool_name,
                    arguments=arguments,
                    skill_path=tool_info.get("skill_path", ""),
                    skill_action=tool_info.get("skill_action", "")
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


class MockToolExecutor(ToolExecutor):
    """
    模拟工具执行器（用于测试）
    
    不实际执行脚本，返回模拟结果。
    """
    
    def execute_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        skill_path: str,
        skill_action: str
    ) -> ExecutionResult:
        """
        模拟执行工具调用
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            skill_path: 技能脚本路径
            skill_action: 技能动作名称
            
        Returns:
            ExecutionResult: 模拟执行结果
        """
        return ExecutionResult(
            success=True,
            tool_name=tool_name,
            result={
                "status": "success",
                "action": skill_action,
                "params": arguments,
                "mock": True
            },
            error=None,
            duration=0.001
        )


def create_tool_registry() -> Dict[str, Dict[str, Any]]:
    """
    创建工具注册表
    
    Returns:
        Dict: 工具注册表 {tool_name: {skill_path, skill_action}}
    """
    from tool_definitions import ALL_TOOLS
    
    registry = {}
    for tool in ALL_TOOLS:
        registry[tool.name] = {
            "skill_path": tool.skill_path,
            "skill_action": tool.skill_action,
            "description": tool.description
        }
    return registry


if __name__ == "__main__":
    print("工具执行器测试")
    print("=" * 60)
    
    registry = create_tool_registry()
    print(f"已注册工具数量: {len(registry)}")
    print("\n工具列表:")
    for name, info in registry.items():
        print(f"  • {name}: {info['skill_action']}")
    
    print("\n模拟执行测试:")
    mock_executor = MockToolExecutor()
    result = mock_executor.execute_tool(
        tool_name="desktop_click",
        arguments={"x": 100, "y": 200},
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="click"
    )
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
