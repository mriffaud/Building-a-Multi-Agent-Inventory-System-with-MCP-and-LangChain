# Building a Multi-Agent Inventory System with MCP and LangChain

Managing inventory across multiple systems—like a store and a warehouse—can quickly become complex. In this article, we’ll explore a practical implementation using LangChain, Azure OpenAI, and FastMCP to create a multi-agent architecture that handles basket operations and warehouse stock synchronisation.
We’ll break down five Python scripts:
* `store_server.py`
* `store_client.py`
* `warehouse_server.py`
* `warehouse_client.py`
* `mcp_client.py`

By the end, you’ll understand how these components interact to form a distributed inventory management system.

## What is MCP and Why Use It?
Imagine trying to connect your AI application to dozens of different tools, databases, calendars, file systems... Each with its own API and authentication quirks. Traditionally, this means writing custom connection for every integration, a process that is time-consuming and error-prone. Model Context Protocol (MCP) solves this problem by acting as a universal adapter for AI applications.

#### What is MCP?
MCP is an open-source standard designed to enable AI applications to interact seamlessly with external systems. We can think of a MCP as the USB-C of AI integrations: just as USB-C provides a single, standard way to connect devices, MCP provides a unified protocol for connecting AI models to tools, data sources and workflows.

At its core, MCP uses a client-server architecture:
* MCP Server: A program that exposes capabilities—such as tools, resources, and prompts—to AI applications.
* MCP Client: A connector inside the host application that maintains a one-to-one connection with an MCP server.
* Host Application: The AI-powered app (we are using a LangChain agent) that orchestrates multiple MCP clients.

This architecture allows an AI agent to call functions (tools), read contextual data (resources), and use predefined templates (prompts) without hardcoding integrations.

#### Why Does MCP Matter?
MCP brings three major benefits:
* Standardisation: Before MCP, developers had to build custom connections for every tool. MCP eliminates this duplication by providing a reusable protocol layer. Once a server is built for a data source, any MCP-compatible client can use it.
* Contextual Intelligence: AI models are only as good as the context they have. Using MCP servers, we can provide rich context documents, database schemas, or inventory data, so the model can make informed decisions. For example, in our project, the warehouse server exposes stock levels, enabling the agent to validate availability before adding items to a basket.
* Composable Workflows: MCP enables modular design. You can combine multiple servers into a single AI-driven workflow. The host application coordinates these servers, maintaining isolation and security boundaries while aggregating context.

#### How Does This Apply to Our Project?
In our inventory system:
* We use `FastMCP` to build lightweight MCP servers for the store and warehouse.
* `LangChain` agents act as the host, interpreting natural language and invoking MCP tools.
* `Azure OpenAI` provides the LLM backbone for reasoning and orchestration.
This combination allows users to manage inventory conversationally while ensuring data consistency across systems. All of this without writing custom APIs for each integration!

## Deep Dive into Components
Now that we understand MCP servers and how they can be useful, let’s roll up our sleeves and look at the actual building blocks of our inventory system. It consists of five Python scripts, each playing a distinct role in orchestrating inventory management through natural language commands:
* Two scripts (`store_server.py` and `warehouse_server.py`) act as MCP servers, exposing tools for basket and stock operations.
* Two scripts (`store_client.py` and `warehouse_client.py`) serve as interactive clients, allowing users to manage these systems conversationally.
* Finally, `mcp_client.py` acts as the orchestrator, bridging the store and warehouse to maintain data consistency.

In this section, we’ll break down each component, explain its responsibilities, and show how they work together to create a seamless, AI-driven workflow. From tool registration to LangChain-powered reasoning, you’ll see how these pieces fit into the bigger picture.

### Store Server
The store server is the backbone of basket management in our system. It runs as an MCP server using FastMCP, exposing a set of tools that allow clients to add, view, and remove items from the basket. This design ensures that basket operations are modular and accessible via natural language commands through the MCP protocol.

#### Purpose
The store server maintains a simple in-memory dictionary called `mcp_basket` to track items and their quantities. By exposing this functionality as MCP tools, any MCP-compatible client can interact with the basket without worrying about implementation details.

#### Code Snippet for Tool Registration
Here’s how the server registers these tools using **FastMCP**:
```python
from fastmcp import FastMCP

# Initialise MCP server
mcp = FastMCP("MCP_STORE")

# Basket to store items
mcp_basket = {}

@mcp.tool()
def add_item(key: str, quantity: int) -> str:
    """Add an item to the basket with specified quantity"""
    mcp_basket[key] = quantity
    return f"Added {key} with quantity: {quantity}"

@mcp.tool()
def get_items() -> dict:
    """Get all items from the basket"""
    return {"items": mcp_basket}

@mcp.tool()
def remove_item(key: str) -> str:
    """Remove an item from the basket"""
    if key in mcp_basket:
        value = mcp_basket.pop(key)
        return f"Removed {key}: {value}"
    return f"Key {key} not found"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)
```

#### How It Works:
The store server operates as a lightweight MCP service that exposes basket management functionality through a standardised protocol. Here’s the step-by-step breakdown:

**Initialisation**
```python
mcp = FastMCP("MCP_STORE")
```
* This creates an MCP server instance named `MCP_STORE`.
* FastMCP handles all the boilerplate for registering tools and serving them over HTTP using the MCP specification.

**Basket State**
```python
mcp_basket = {}
```
* The basket is represented as a simple Python dictionary.
* Keys are item names and values are quantities.
* This in-memory structure makes operations fast and straightforward.

**Tool Registration**

Each function decorated with `@mcp.tool()` becomes an MCP tool:
* `add_item`: Updates the dictionary with the item and quantity.
* `get_items`: Returns the entire basket as a JSON-friendly dictionary.
* `remove_item`: Deletes the item if it exists, returning a confirmation message.
These tools are automatically exposed to any MCP client that connects to this server.

**Integration with LangChain**

* LangChain agents discover these tools dynamically via the MCP client.
* When a user types:  
    *“Add an item apple of quantity 3 to the basket”*,  
    the agent interprets the intent and calls `add_item` on the MCP server.
* This decouples natural language understanding from business logic, ensuring modularity.


### Store Client
Purpose: interactive CLI for basket operations.
How it uses LangChain + Azure GPT-5 Nano.
Example command and agent behaviour.

### Warehouse Server
Purpose: stock management.
Tools: get_products, check_product, update_quantity, etc.
Code snippet for adding/removing products.

### Warehouse Client
Similar to store client but for warehouse.
Example workflow.

### The Orchestrator: MCP Client
The orchestrator.
How it validates stock before adding to basket.
Helper functions like extract_quantity.
Example end-to-end flow.

## Why This Architecture Works?
Natural language interface.
Distributed design.
AI-powered orchestration.

## Future Enhancements
Persistent storage.
Authentication.
Better quantity parsing (e.g., “ten” vs “10”).

## Conclusion
Recap benefits.
Encourage experimentation with MCP + LangChain.

## Ressources
- https://medium.com/@anoopninangeorge/building-a-remote-mcp-server-a-mcp-client-with-fastmcp-langchain-langgraph-17cf0e8d043b
- https://modelcontextprotocol.io/docs/getting-started/intro
- https://modelcontextprotocol.io/docs/learn/architecture
- https://modelcontextprotocol.io/docs/learn/server-concepts
- https://modelcontextprotocol.io/docs/learn/client-concepts
- https://gofastmcp.com/getting-started/welcome
- https://gofastmcp.com/servers/server





