from src.mcp_manager import mcp_manager
import json


def connect_mcp_server(command: str, args: str = "[]"):
    """
    连接到一个基于 Stdio 的 MCP (Model Context Protocol) 服务器。
    连接成功后，你可以使用list_mcp_tools 查看可用工具

    参数：
        command: 可执行命令 (例如 "uvx", "python", "node")
        args: JSON 格式的参数列表字符串 (例如 '["mcp-server-git", "--repository", "."]')

    返回：
        连接状态信息
    """
    try:
        args_list = json.loads(args)
        if not isinstance(args_list, list):
            return "Error: args must be a JSON list string"
        mcp_manager.connect(command, args_list)
        return f"Successfully connected to MCP Server: {command} {args_list}"
    except Exception as e:
        return f"Connection failed: {str(e)}"
