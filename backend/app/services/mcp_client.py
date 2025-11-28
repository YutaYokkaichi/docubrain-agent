import sys
import os
import traceback
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        """MCPサーバー(server.py)をサブプロセスとして起動し接続する"""
        
        # 【修正】Dockerコンテナ内の絶対パスを直接指定 (これが一番確実！)
        server_path = "/app/app/mcp/server.py"
        
        print(f"🔧 [Target Path] {server_path}")

        # 存在確認
        if not os.path.exists(server_path):
            print(f"❌ [ERROR] server.py NOT FOUND at {server_path}")
            # デバッグ: ディレクトリの中身を確認
            try:
                print(f"📂 /app/app contains: {os.listdir('/app/app')}")
                if os.path.exists('/app/app/mcp'):
                    print(f"📂 /app/app/mcp contains: {os.listdir('/app/app/mcp')}")
            except Exception as e:
                print(f"Debug ls failed: {e}")
            raise FileNotFoundError(f"MCP Server not found at {server_path}")

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_path],
            env=dict(os.environ)
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.read, self.write = stdio_transport
            
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))
            
            await self.session.initialize()
            print("✅ Connected to MCP Server (Internal)")
            
        except Exception as e:
            print(f"❌ [ERROR] Failed to connect/initialize MCP:")
            traceback.print_exc()
            await self.close()
            raise e

    async def list_tools(self):
        if not self.session:
            raise RuntimeError("MCP session is not connected")
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, name: str, arguments: dict):
        if not self.session:
            raise RuntimeError("MCP session is not connected")
        result = await self.session.call_tool(name, arguments)
        return result.content

    async def close(self):
        if self.exit_stack:
            await self.exit_stack.aclose()
            print("🛑 MCP Client closed")

mcp_client = MCPClient()