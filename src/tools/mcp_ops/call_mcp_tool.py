import json
from src.mcp_manager import mcp_manager


def call_mcp_tool(tool_name: str, arguments: str):
    """
    调用 MCP 服务器上的特定工具

    参数：
        tool_name: 工具名称 （从 list_mcp_tools 获取）
        arguments: JSON 格式的参数字典字符串 (例如'{"repo_path": "."}')
    
    返回：
        工具执行结果
    """
    try:
        args_dict = json.loads(arguments)
        if not isinstance(args_dict, dict):
            return "Error: arguments must be a JSON object string"
        result = mcp_manager.call_tool(tool_name, args_dict)
        return f"MCP Tool Output:\n{result}"
    except Exception as e:
        return f"Error calling tool {tool_name}: {str(e)}"