import asyncio
import os
from typing import Any
import re

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI
#from langchain.agents import create_agent
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
    """Interactive MCP client for store and warehouse."""
    client = MultiServerMCPClient({
        "mcpstore": {
            "url": "http://127.0.0.1:8001/mcp",
            "transport": "streamable_http"
        },
        "mcpwarehouse": {
            "url": "http://127.0.0.1:8002/mcp",
            "transport": "streamable_http"
        }
    })

    tools = await client.get_tools()
    agent = create_react_agent(model, tools)

    print("Welcome! Type 'exit' to quit.")
    while True:
        action = input("\nChoose action (add/remove/view-basket/view-warehouse): ").strip().lower()
        if action == "exit":
            print("Goodbye!")
            break

        if action == "add":
            item = input("Item: ").strip()
            quantity = input("Quantity: ").strip()
            if not quantity.isdigit() or int(quantity) <= 0:
                print("Quantity must be a positive integer.")
                continue
            quantity = int(quantity)

            # Check warehouse stock
            stock_query = f"Check if {item} exists and its quantity in warehouse"
            stock_response = await agent.ainvoke({"messages": stock_query})
            stock_text = extract_ai_message(stock_response)

            if "not found" in stock_text.lower():
                print(f"{item} is not available in the warehouse.")
                continue

            # Extract available quantity
            available_qty = extract_quantity(stock_text)
            if available_qty < quantity:
                print(f"Not enough stock. Available: {available_qty}")
                continue

            # Add to basket
            basket_query = f"Add an item {item} of quantity {quantity} to mcpstore website basket"
            basket_response = await agent.ainvoke({"messages": basket_query})
            process_and_print_response(basket_response)

            # Update warehouse
            new_qty = available_qty - quantity
            update_query = f"Update {item} quantity to {new_qty} in warehouse"
            await agent.ainvoke({"messages": update_query})

        elif action == "remove":
            item = input("Item to remove: ").strip()
            quantity = input("Quantity to remove: ").strip()
            if not quantity.isdigit() or int(quantity) <= 0:
                print("Quantity must be a positive integer.")
                continue
            quantity = int(quantity)

            # Check basket stock
            basket_query = f"Check if {item} exists and its quantity in basket"
            basket_response = await agent.ainvoke({"messages": basket_query})
            basket_text = extract_ai_message(basket_response)
            basket_qty = extract_quantity(basket_text)

            if basket_qty == 0:
                print(f"{item} is not in the basket.")
                continue
            if quantity > basket_qty:
                print(f"Cannot remove {quantity}. Only {basket_qty} in basket.")
                continue

            # Remove specified quantity from basket
            remove_query = f"Remove {quantity} of {item} from basket"
            remove_response = await agent.ainvoke({"messages": remove_query})
            process_and_print_response(remove_response)

            # Update warehouse
            stock_query = f"Check if {item} exists and its quantity in warehouse"
            stock_response = await agent.ainvoke({"messages": stock_query})
            available_qty = extract_quantity(extract_ai_message(stock_response))
            new_qty = available_qty + quantity
            update_query = f"Update {item} quantity to {new_qty} in warehouse"
            await agent.ainvoke({"messages": update_query})


        elif action == "view-basket":
            query = "Get the mcpstore website basket contents"
            response = await agent.ainvoke({"messages": query})
            process_and_print_response(response)

        elif action == "view-warehouse":
            query = "Get all products and quantities from warehouse"
            response = await agent.ainvoke({"messages": query})
            process_and_print_response(response)

        else:
            print("Invalid action.")

# Helper functions
def extract_ai_message(response):
    for message in response["messages"]:
        if type(message).__name__ == "AIMessage" and message.content:
            return message.content
    return ""

def extract_quantity(text):
    # Simple parser for "available: X"
    import re
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0

def extract_removed_quantity(response):
    text = extract_ai_message(response)
    match = re.search(r"Removed\s+(\w+)\s*:\s*(\d+)", text)
    if match:
        item = match.group(1)
        quantity = int(match.group(2))
        return {"item": item, "quantity": quantity}
    return None


def process_and_print_response(response):
    print("\n------------Response------------")
    print(extract_ai_message(response))
    print("--------------------------------")

if __name__ == "__main__":
    asyncio.run(main())