import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Any

async def main():
    # Initialize the MCP client
    global tools
    mcp_client = MultiServerMCPClient(
        {
            "local_mcp_server":
                {
                    "url": "http://localhost:9000/mcp",
                    "transport": "streamable-http",
                }
        }
    )
    try:
        print("Fetching tools from MCP server...")
        tools = await mcp_client.get_tools()
        for tool in tools:
            print(f"Tool: {tool.name}, Description: {tool.description}")
    except Exception as ex:
        print(ex)

    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    )

    agent = create_agent(llm, tools)

    agnet_input: dict[str, Any] = {
        "messages": [
            HumanMessage(
                content="Call the get_items tool and show me the items. "
                        "Please display details of itemId 1 and format result in markdown."
            )
        ]
    }

    response = await agent.ainvoke(agnet_input)

    print("\nFinal response:")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
