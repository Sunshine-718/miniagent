import asyncio
import threading
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MCPManager, cls).__new__(cls)
                cls._instance.initialized = False
            return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.exit_stack = AsyncExitStack()
        self.session = None
        self.server_params = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.initialized = True

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _connect(self, command: str, args: list, env: dict = None):
        """内部异步连接逻辑"""
        self.server_params = StdioServerParameters(command=command,
                                                   args=args,
                                                   env=env)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()
        return "Connected to MCP Server"

    def connect(self, command: str, args: list = None, env: dict = None):
        """同步连接接口"""
        if args is None:
            args = []
        future = asyncio.run_coroutine_threadsafe(
            self._connect(command, args, env), self.loop
        )
        return future.result()

    async def _list_tools(self):
        if not self.session:
            return "Error: No MCP session active"
        result = await self.session.list_tools()
        return result.tools

    def list_tools(self):
        future = asyncio.run_coroutine_threadsafe(self._list_tools(), self.loop)
        return future.result()

    async def _call_tool(self, name: str, arguments: dict):
        if not self.session:
            return "Error: No MCP session active."
        result = await self.session.call_tool(name, arguments)
        return result.content

    def call_tool(self, name: str, arguments: dict):
        future = asyncio.run_coroutine_threadsafe(
            self._call_tool(name, arguments), self.loop
        )
        res = future.result()
        text_content = []
        for content in res:
            if content.type == 'text':
                text_content.append(content.text)
        return "\n".join(text_content)


mcp_manager = MCPManager()
