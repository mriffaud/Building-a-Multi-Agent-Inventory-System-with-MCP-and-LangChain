from typing import Any
import asyncio
import json
import os
import re


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
    """Main function to process queries using the MCP client interactively."""
    client = MultiServerMCPClient({
        "mcpstore": {
            "url": "http://127.0.0.1:8001/mcp",  # Replace with the remote server's URL
            "transport": "streamable_http"
        }
    })
    tools = await client.get_tools()
    agent = create_react_agent(model, tools)

    print("Welcome to MCP Store! Type 'exit' to quit.")
    while True:
        action = input("\nAdd/remove/view/exit: ").strip().lower()
        if action == "exit":
            print("Exiting MCP Store. Goodbye!")
            break
        if action == "add":
            item = input("Item: ").strip()
            quantity = input("Quantity: ").strip()
            query = f"Add an item {item} of quantity {quantity} to mcpstore website basket"
        elif action == "remove":
            item = input("Item to remove: ").strip()
            quantity = input("Quantity to remove: ").strip()
            if not quantity.isdigit() or int(quantity) <= 0:
                print("Quantity must be a positive integer.")
                continue
            quantity = int(quantity)
            check_query = f"Check if {item} exists and its quantity in basket"
            check_response = await agent.ainvoke({"messages": check_query})
            current_qty = extract_quantity(extract_ai_message(check_response))
            if current_qty == 0:
                print(f"{item} is not in the basket.")
                continue
            if quantity > current_qty:
                print(f"Cannot remove {quantity}. Only {current_qty} in basket.")
                continue
            if quantity == current_qty:
                remove_query = f"Remove {item} from basket"
            else:
                new_qty = current_qty - quantity
                remove_query = f"Update {item} quantity to {new_qty} in basket"

            response = await agent.ainvoke({"messages": remove_query})
            process_and_print_response(response)
        elif action == "view":
            query = "Get the mcpstore website basket contents"
        else:
            print("Invalid action.")
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

def extract_quantity(text: str) -> int:
    """
    Extracts the first integer quantity from the given text.
    Returns 1 if no quantity is found.
    """
    match = re.search(r"\b\d+\b", text)
    return int(match.group()) if match else 1


if __name__ == "__main__":
    asyncio.run(main())
    
