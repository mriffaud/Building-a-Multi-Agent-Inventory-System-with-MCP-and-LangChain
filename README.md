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
Break down each script in its own subsection:

### Store Server (store_server.py)
Purpose: basket management.
Tools exposed: add_item, get_items, remove_item.
Code snippet for tool registration.

### Store Client (store_client.py)
Purpose: interactive CLI for basket operations.
How it uses LangChain + Azure GPT-5 Nano.
Example command and agent behaviour.

### Warehouse Server (warehouse_server.py)
Purpose: stock management.
Tools: get_products, check_product, update_quantity, etc.
Code snippet for adding/removing products.

### Warehouse Client (warehouse_client.py)
Similar to store client but for warehouse.
Example workflow.

### MCP Client (mcp_client.py)
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





