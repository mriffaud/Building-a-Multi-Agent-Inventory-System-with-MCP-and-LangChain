from typing import Any
import asyncio
import json
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

# Configure OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR OPEN AI API KEY"

# Initialise model
model = AzureChatOpenAI(
    azure_endpoint="YOUR OPEN AI ENDPOINT",
    api_version="2024-02-01",
    model_name="gpt-5-nano",
    temperature=0,
    )


async def main():
    """Interactive warehouse client to manage inventory."""
    client = MultiServerMCPClient({
        "mcp_warehouse": {
        "url": "http://127.0.0.1:8002/mcp",
        "transport": "streamable_http",
        },
        })

    tools = await client.get_tools()
    agent = create_react_agent(model, tools)

    print("Welcome to the Warehouse! Type 'exit' to quit.")
    while True:
        action = input("\nAdd/remove/view/exit: ").strip().lower()
        if action == "exit":
            print("Exiting the Warehouse. Goodbye!")
            break
        if action == "add":
            item = input("Item: ").strip()
            quantity = input("Quantity: ").strip()
            query = f"Add {quantity} units of {item} to the warehouse inventory"
        elif action == "remove":
            item = input("Item: ").strip()
            quantity = input("Quantity: ").strip()
            query = f"Remove {quantity} units of {item} from the warehouse inventory"
        elif action == "view":
            query = "Get the current warehouse inventory"
        else:
            print("Invalid action. Please choose add/remove/view/exit.")
            continue

        response = await agent.ainvoke({"messages": query})
        process_and_print_response(response)

def serialise_response(obj: Any) -> Any:
    """Helper function to make the response JSON serialisable."""
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


def print_tool_calls(response):
    """Print tool calls from the response object."""
    for message in response["messages"]:
        if hasattr(message, "additional_kwargs") and message.additional_kwargs.get("tool_calls"):
            tool_calls = message.tool_calls
            print("\n------------Tool Calls------------")
            for tool_call in tool_calls:
                print(f"Tool Name: {tool_call['name']}")
                print(f"Tool ID: {tool_call['id']}")
                print("Arguments:", json.dumps(tool_call['args'], indent=2))
                print("------------------------")


def print_ai_messages(response):
    """Print all non-empty AI messages from the response."""
    for message in response["messages"]:
        if type(message).__name__ == "AIMessage" and message.content:
            print("\n------------AI Message------------")
            print(f"Content: {message.content}")
            print("--------------------------------")

def process_and_print_response(response):
        """Process and print the response from the agent."""
        #json_response = json.dumps(response, default=serialise_response, indent=2)
        #print("\n------------Json Response------------")
        #print(json_response)
        print_tool_calls(response)   
        print_ai_messages(response)


if __name__ == "__main__":
    asyncio.run(main())