"""
tool_definitions.py - Ollama工具调用定义模块

将OpenClaw桌面控制技能转换为Ollama原生工具调用格式。
支持Ollama API的工具定义规范。

作者: AI Assistant
版本: 1.0.0
日期: 2026-02-17
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ToolParameter:
    """
    工具参数定义类
    
    Attributes:
        name: 参数名称
        param_type: 参数类型 (string, integer, number, boolean, array, object)
        description: 参数描述
        required: 是否必需
        enum: 枚举值列表（可选）
        default: 默认值（可选）
    """
    name: str
    param_type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None
    default: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将参数定义转换为Ollama API格式
        
        Returns:
            Dict: Ollama工具参数格式字典
        """
        result = {
            "type": self.param_type,
            "description": self.description
        }
        if self.enum:
            result["enum"] = self.enum
        if self.default is not None:
            result["default"] = self.default
        return result


@dataclass
class ToolDefinition:
    """
    工具定义类
    
    Attributes:
        name: 工具名称
        description: 工具描述
        parameters: 参数列表
        skill_path: 关联的技能脚本路径
        skill_action: 技能动作名称
    """
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    skill_path: str = ""
    skill_action: str = ""
    
    def to_ollama_format(self) -> Dict[str, Any]:
        """
        转换为Ollama原生工具调用格式
        
        Returns:
            Dict: Ollama工具定义格式
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_dict()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


DESKTOP_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="desktop_screenshot",
        description="截取屏幕截图，可指定保存路径和区域。支持全屏截图和区域截图。",
        parameters=[
            ToolParameter("path", "string", "截图保存路径，例如: /tmp/screenshot.png", default="/tmp/screenshot.png"),
            ToolParameter("region", "array", "截图区域 [x, y, width, height]，不指定则为全屏", required=False),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="screenshot"
    ),
    ToolDefinition(
        name="desktop_move",
        description="移动鼠标光标到指定坐标位置",
        parameters=[
            ToolParameter("x", "integer", "目标X坐标", required=True),
            ToolParameter("y", "integer", "目标Y坐标", required=True),
            ToolParameter("duration", "number", "移动持续时间(秒)", default=0.2),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="move"
    ),
    ToolDefinition(
        name="desktop_click",
        description="在指定位置执行鼠标点击操作",
        parameters=[
            ToolParameter("x", "integer", "点击位置X坐标", required=True),
            ToolParameter("y", "integer", "点击位置Y坐标", required=True),
            ToolParameter("button", "string", "鼠标按钮", enum=["left", "right", "middle"], default="left"),
            ToolParameter("clicks", "integer", "点击次数", default=1),
            ToolParameter("duration", "number", "点击持续时间(秒)", default=0.1),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="click"
    ),
    ToolDefinition(
        name="desktop_double_click",
        description="在指定位置执行鼠标双击操作",
        parameters=[
            ToolParameter("x", "integer", "双击位置X坐标", required=True),
            ToolParameter("y", "integer", "双击位置Y坐标", required=True),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="double_click"
    ),
    ToolDefinition(
        name="desktop_right_click",
        description="在指定位置执行鼠标右键点击操作",
        parameters=[
            ToolParameter("x", "integer", "右键点击位置X坐标", required=True),
            ToolParameter("y", "integer", "右键点击位置Y坐标", required=True),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="right_click"
    ),
    ToolDefinition(
        name="desktop_drag",
        description="执行鼠标拖拽操作，从起点拖拽到终点",
        parameters=[
            ToolParameter("start", "array", "起点坐标 [x, y]", required=True),
            ToolParameter("end", "array", "终点坐标 [x, y]", required=True),
            ToolParameter("duration", "number", "拖拽持续时间(秒)", default=0.5),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="drag"
    ),
    ToolDefinition(
        name="desktop_scroll",
        description="执行鼠标滚轮滚动操作",
        parameters=[
            ToolParameter("direction", "string", "滚动方向", enum=["up", "down"], default="down"),
            ToolParameter("amount", "integer", "滚动量", default=3),
            ToolParameter("x", "integer", "滚动位置X坐标(可选)", required=False),
            ToolParameter("y", "integer", "滚动位置Y坐标(可选)", required=False),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="scroll"
    ),
    ToolDefinition(
        name="desktop_position",
        description="获取当前鼠标光标位置",
        parameters=[],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="position"
    ),
    ToolDefinition(
        name="desktop_type",
        description="输入文本内容，支持中英文输入",
        parameters=[
            ToolParameter("text", "string", "要输入的文本内容", required=True),
            ToolParameter("interval", "number", "字符输入间隔(秒)", default=0.02),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="type"
    ),
    ToolDefinition(
        name="desktop_key",
        description="按下并释放单个按键",
        parameters=[
            ToolParameter("key", "string", "按键名称，如: enter, escape, tab, space等", required=True),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="key"
    ),
    ToolDefinition(
        name="desktop_hotkey",
        description="执行组合键操作，如复制(Ctrl+C)、粘贴(Ctrl+V)等",
        parameters=[
            ToolParameter("keys", "array", "组合键列表，如: ['ctrl', 'c'] 或 ['alt', 'f4']", required=True),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="hotkey"
    ),
    ToolDefinition(
        name="desktop_locate",
        description="在屏幕上定位指定图像的位置",
        parameters=[
            ToolParameter("image", "string", "要定位的图像文件路径", required=True),
            ToolParameter("confidence", "number", "匹配置信度(0-1)", default=0.9),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="locate"
    ),
    ToolDefinition(
        name="desktop_locate_and_click",
        description="在屏幕上定位指定图像并点击其中心位置",
        parameters=[
            ToolParameter("image", "string", "要定位的图像文件路径", required=True),
            ToolParameter("confidence", "number", "匹配置信度(0-1)", default=0.9),
        ],
        skill_path="skills/fusion-desktop/scripts/desktop.py",
        skill_action="locate_and_click"
    ),
]

SCREEN_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="screen_screenshot_base64",
        description="截取屏幕并返回Base64编码图像",
        parameters=[
            ToolParameter("region", "array", "截图区域 [x, y, width, height](可选)", required=False),
        ],
        skill_path="skills/fusion-screen/scripts/screen.py",
        skill_action="screenshot_base64"
    ),
    ToolDefinition(
        name="screen_ocr",
        description="对屏幕指定区域进行OCR文字识别",
        parameters=[
            ToolParameter("region", "array", "识别区域 [x, y, width, height](可选)", required=False),
            ToolParameter("lang", "string", "OCR语言，如: chi_sim, eng", default="chi_sim"),
        ],
        skill_path="skills/fusion-screen/scripts/screen.py",
        skill_action="ocr"
    ),
    ToolDefinition(
        name="screen_get_size",
        description="获取屏幕尺寸信息",
        parameters=[],
        skill_path="skills/fusion-screen/scripts/screen.py",
        skill_action="get_screen_size"
    ),
]

CLIPBOARD_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="clipboard_copy",
        description="复制文本到剪贴板",
        parameters=[
            ToolParameter("text", "string", "要复制的文本内容", required=True),
        ],
        skill_path="skills/fusion-clipboard/scripts/clipboard.py",
        skill_action="copy"
    ),
    ToolDefinition(
        name="clipboard_paste",
        description="从剪贴板粘贴文本",
        parameters=[],
        skill_path="skills/fusion-clipboard/scripts/clipboard.py",
        skill_action="paste"
    ),
    ToolDefinition(
        name="clipboard_get",
        description="获取剪贴板当前内容",
        parameters=[],
        skill_path="skills/fusion-clipboard/scripts/clipboard.py",
        skill_action="get"
    ),
    ToolDefinition(
        name="clipboard_clear",
        description="清空剪贴板内容",
        parameters=[],
        skill_path="skills/fusion-clipboard/scripts/clipboard.py",
        skill_action="clear"
    ),
]

WINDOW_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="window_list",
        description="列出所有打开的窗口",
        parameters=[],
        skill_path="skills/fusion-window/scripts/window.py",
        skill_action="list"
    ),
    ToolDefinition(
        name="window_find",
        description="根据标题查找窗口",
        parameters=[
            ToolParameter("title", "string", "窗口标题(支持模糊匹配)", required=True),
        ],
        skill_path="skills/fusion-window/scripts/window.py",
        skill_action="find"
    ),
    ToolDefinition(
        name="window_activate",
        description="激活(前置)指定窗口",
        parameters=[
            ToolParameter("title", "string", "窗口标题", required=True),
        ],
        skill_path="skills/fusion-window/scripts/window.py",
        skill_action="activate"
    ),
    ToolDefinition(
        name="window_close",
        description="关闭指定窗口",
        parameters=[
            ToolParameter("title", "string", "窗口标题", required=True),
        ],
        skill_path="skills/fusion-window/scripts/window.py",
        skill_action="close"
    ),
    ToolDefinition(
        name="window_minimize",
        description="最小化指定窗口",
        parameters=[
            ToolParameter("title", "string", "窗口标题", required=True),
        ],
        skill_path="skills/fusion-window/scripts/window.py",
        skill_action="minimize"
    ),
    ToolDefinition(
        name="window_maximize",
        description="最大化指定窗口",
        parameters=[
            ToolParameter("title", "string", "窗口标题", required=True),
        ],
        skill_path="skills/fusion-window/scripts/window.py",
        skill_action="maximize"
    ),
]

BROWSER_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="browser_open",
        description="打开浏览器并导航到指定URL",
        parameters=[
            ToolParameter("url", "string", "要打开的网址URL", required=True),
            ToolParameter("headless", "boolean", "是否使用无头模式", default=False),
        ],
        skill_path="skills/fusion-browser/scripts/browser.js",
        skill_action="open"
    ),
    ToolDefinition(
        name="browser_screenshot",
        description="截取当前网页的截图",
        parameters=[
            ToolParameter("path", "string", "截图保存路径", default="/tmp/browser_screenshot.png"),
        ],
        skill_path="skills/fusion-browser/scripts/browser.js",
        skill_action="screenshot"
    ),
    ToolDefinition(
        name="browser_close",
        description="关闭浏览器",
        parameters=[],
        skill_path="skills/fusion-browser/scripts/browser.js",
        skill_action="close"
    ),
]

ALL_TOOLS = DESKTOP_TOOLS + SCREEN_TOOLS + CLIPBOARD_TOOLS + WINDOW_TOOLS + BROWSER_TOOLS


def get_tool_by_name(name: str) -> Optional[ToolDefinition]:
    """
    根据名称获取工具定义
    
    Args:
        name: 工具名称
        
    Returns:
        ToolDefinition: 工具定义，未找到返回None
    """
    for tool in ALL_TOOLS:
        if tool.name == name:
            return tool
    return None


def get_all_tools_ollama_format() -> List[Dict[str, Any]]:
    """
    获取所有工具的Ollama格式定义
    
    Returns:
        List[Dict]: Ollama工具定义列表
    """
    return [tool.to_ollama_format() for tool in ALL_TOOLS]


def get_tools_by_category(category: str) -> List[ToolDefinition]:
    """
    根据类别获取工具列表
    
    Args:
        category: 工具类别 (desktop, screen, clipboard, window, browser)
        
    Returns:
        List[ToolDefinition]: 工具定义列表
    """
    category_map = {
        "desktop": DESKTOP_TOOLS,
        "screen": SCREEN_TOOLS,
        "clipboard": CLIPBOARD_TOOLS,
        "window": WINDOW_TOOLS,
        "browser": BROWSER_TOOLS,
    }
    return category_map.get(category, [])


def print_tools_info():
    """
    打印所有工具信息
    """
    print("=" * 60)
    print("OpenClaw Ollama工具调用定义")
    print("=" * 60)
    
    categories = {
        "桌面控制": DESKTOP_TOOLS,
        "屏幕操作": SCREEN_TOOLS,
        "剪贴板": CLIPBOARD_TOOLS,
        "窗口管理": WINDOW_TOOLS,
        "浏览器": BROWSER_TOOLS,
    }
    
    for category, tools in categories.items():
        print(f"\n【{category}】({len(tools)}个工具)")
        print("-" * 40)
        for tool in tools:
            print(f"  • {tool.name}")
            print(f"    {tool.description}")
    
    print("\n" + "=" * 60)
    print(f"总计: {len(ALL_TOOLS)}个工具")
    print("=" * 60)


if __name__ == "__main__":
    print_tools_info()
    print("\n示例工具定义(Ollama格式):")
    print(json.dumps(DESKTOP_TOOLS[0].to_ollama_format(), indent=2, ensure_ascii=False))
