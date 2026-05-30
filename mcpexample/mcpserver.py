import mcp
from fastmcp import FastMCP
import requests


class MCPServer:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        self.mcp = FastMCP("MCP Server")

    def start(self):
        self.register_tool()
        self.mcp.run(transport="streamable-http",host=self.host, port=self.port)

    def register_tool(self):
        """Registers a function as an MCP tool."""
        @self.mcp.tool
        def echo(message: str) -> str:
            """Echoes the input message."""
            return f"Echo: {message}"

        @self.mcp.tool
        def add(a: int, b: int) -> int:
            """Adds two numbers."""
            return a + b

        @self.mcp.tool
        def multiply(a: int, b: int) -> int:
            """Multiplies two numbers."""
            return a * b

        @self.mcp.tool
        def reverse_string(s: str) -> str:
            """Reverses the input string."""
            return s[::-1]

        @self.mcp.tool
        def subtract(a: int, b: int) -> int:
            """Subtracts two numbers."""
            return a - b

        @self.mcp.tool
        def get_items() -> list:
            """Returns a list of items."""
            data = requests.get(f"http://localhost:8000/items").json()
            print(data)
            return data

        #f64a0f69e5d94b418f78c389253fecfd
        @self.mcp.tool
        def get_item(item_id: int) -> dict:
            """Returns a specific item by ID."""
            return requests.get(f"http://localhost:8000/items/{item_id}").json()

if __name__ == "__main__":
    server = MCPServer()
    server.start()


