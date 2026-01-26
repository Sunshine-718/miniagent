import json
from src.mcp_manager import mcp_manager


def list_mcp_tools():
    """
    列出当前已连接的 MCP 服务器提供的所有可用工具
    再调用此工具前，请确保已使用 connect_mcp_server 建立连接
    
    返回：
        工具列表及描述
    """
    try:
        tools = mcp_manager.list_tools()
        if isinstance(tools, str) and tools.startswith("Error"):
            return tools
        result = ["Available MCP Tools:"]
        for tool in tools:
            result.append(f"- {tool.name}: {tool.description}")
            result.append(f"    Schema: {json.dumps(tool.inputSchema, ensure_ascii=False)}")
        return '\n'.join(result)
    except Exception as e:
        return f"Error listing tools: {str(e)}"
