from mcp.server.fastmcp import FastMCP

# MCPサーバーの定義
mcp = FastMCP("MathServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの数を足し算します"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """2つの数を掛け算します"""
    return a * b

if __name__ == "__main__":
    # 標準入出力(stdio)を使って通信します
    mcp.run()