# Building a Multi-Agent Inventory System with MCP and LangChain

Managing inventory across multiple systems—like a store and a warehouse—can quickly become complex. In this article, we’ll explore a practical implementation using LangChain, Azure OpenAI, and FastMCP to create a multi-agent architecture that handles basket operations and warehouse stock synchronisation.
We’ll break down five Python scripts:
* `store_server.py`
* `store_client.py`
* `warehouse_server.py`
* `warehouse_client.py`
* `mcp_client.py`

By the end, you’ll understand how these components interact to form a distributed inventory management system.

---
## Table of Content
1. [What is MCP and Why Use It?](#MCP)
2. [Prerequisites](#Prerequisites)
3. [Deep Dive into Components](#Components)
    1. [Store Server](#StoreServer)
    2. [Store Client](#StoreClient)
    3. [Warehouse Server](#WarehouseServer)
    4. [Warehouse Client](#WarehouseClient)
    5. [The Orchestrator](#Orchestrator)
4. [Future Enhancements](#FutureEnhancements)
5. [Conclusion](#Conclusion)
6. [Ressources](#Ressources)

---
<a name="MCP"></a>
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

---
<a name="Prerequisites"></a>
## Prerequisites
Before you begin, ensure you have the necessary infrastructure and tools in place. These scripts rely on a Large Language Model (LLM) deployed via Azure OpenAI Service, so you’ll need an active Azure subscription, a provisioned resource, and access credentials (API key and endpoint URL). 

---
<a name="Components"></a>
## Deep Dive into Components
Now that we understand MCP servers and how they can be useful, let’s roll up our sleeves and look at the actual building blocks of our inventory system. It consists of five Python scripts, each playing a distinct role in orchestrating inventory management through natural language commands:
* Two scripts (`store_server.py` and `warehouse_server.py`) act as MCP servers, exposing tools for basket and stock operations.
* Two scripts (`store_client.py` and `warehouse_client.py`) serve as interactive clients, allowing users to manage these systems conversationally.
* Finally, `mcp_client.py` acts as the orchestrator, bridging the store and warehouse to maintain data consistency.

In this section, we’ll break down each component, explain its responsibilities, and show how they work together to create a seamless, AI-driven workflow. From tool registration to LangChain-powered reasoning, you’ll see how these pieces fit into the bigger picture.

<a name="StoreServer"></a>
### Store Server
The store server is the backbone of basket management in our system. It runs as an MCP server using FastMCP, exposing a set of tools that allow clients to add, view, and remove items from the basket. This design ensures that basket operations are modular and accessible via natural language commands through the MCP protocol.

#### Purpose
The store server maintains a simple in-memory dictionary called `mcp_basket` to track items and their quantities. By exposing this functionality as MCP tools, any MCP-compatible client can interact with the basket without worrying about implementation details.

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

<a name="StoreServer"></a>
### Store Server 
The store server is the backbone of basket management in our system. It runs as an MCP server using FastMCP, exposing a set of tools that allow clients to add, view, and remove items from the basket. This design ensures that basket operations are modular and accessible via natural language commands through the MCP protocol.

#### Purpose
The store server maintains a simple in-memory dictionary called `mcp_basket` to track items and their quantities. By exposing this functionality as MCP tools, any MCP-compatible client can interact with the basket without worrying about implementation details.

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

<a name="StoreClient"></a>
### Store Client 
The store client is an interactive command-line interface that connects to the MCP store server and allows users to manage their basket through a structured prompt sequence.

#### Purpose
The store client enables basket operations such as adding, removing, and viewing items. It ensures clarity by prompting the user for each required input (action, item name, quantity) rather than relying on free-form text interpretation.

#### How It Works:
* Azure GPT-5 Nano is still used as the reasoning engine behind the LangChain agent, but its role is limited to orchestrating MCP tool calls based on structured queries.
* LangChain wraps the MCP tools into a react-style agent using `create_react_agent`.
* The client connects to the MCP store server via `MultiServerMCPClient`, retrieves available tools, and uses them when the user selects an action.

The workflow is deterministic:
1.  Prompt user for an action: `add`, `remove`, `view`, or `exit`.
2.  If `add`:
    *   Prompt for item name (e.g. `apple`).
    *   Prompt for quantity (e.g. `5`).
    *   Construct a query like:
            Add an item apple of quantity 5 to mcpstore website basket
    *   Pass this query to the agent, which invokes the `add_item` tool on the MCP server.
3.  Display the server’s response.

**Example Interaction**

    Welcome to MCP Store! Type 'exit' to quit.

    Add/remove/view/exit: add
    Item: apple
    Quantity: 5
    Added apple with quantity: 5

Behind the scenes:
*   The agent maps the query to the `add_item` tool.
*   Sends a request to the MCP server.
*   Receives and prints the confirmation message.

<a name="WarehouseServer"></a>
### Warehouse Server 
The warehouse server plays a role very similar to the store server, but instead of managing a basket, it manages the entire stock inventory. Like the store server, it runs as an MCP server using FastMCP, and exposes its functionality through MCP tools so that clients can interact with it in a structured, protocol-driven way.

#### Purpose
Just as the store server maintains `mcp_basket`, the warehouse server maintains an in-memory dictionary called `warehouse_inventory`. This dictionary holds product names as keys and their available quantities as values. By exposing this data through MCP tools, the warehouse server becomes a central point for stock operations without requiring custom APIs.

#### How It Works:
The setup is almost identical to the store server:

**Initialisation**

```python
mcp = FastMCP("MCP_WAREHOUSE")
```

This creates an MCP server instance named `MCP_WAREHOUSE`, just like `MCP_STORE` for the basket.

**Inventory State**:  
Instead of an empty basket, the warehouse starts with a predefined dictionary of products and quantities:
   
```python
warehouse_inventory = {
    "apple": 100,
    "banana": 50,
    "orange": 75,
    "grapes": 30,
    "mango": 20,
}
```

**Tool Registration**:  
The concept is the same as for the store server—functions decorated with `@mcp.tool()` become callable MCP tools. The difference lies in the operations:
* `get_products`: Lists all products and quantities.
* `check_product`: Checks if a product exists and its quantity.
* `update_quantity`: Updates the quantity of an existing product.
* `add_product`: Adds a new product to the inventory.
* `remove_product`: Removes a product from the inventory.

These tools are automatically exposed to any MCP client, just like the basket tools.

<a name="WarehouseClient"></a>
### Warehouse Client

The warehouse client serves the same fundamental purpose as the store client—providing an interactive interface for managing operations—but its focus is on stock control rather than basket management. Like the store client, it connects to an MCP server, uses LangChain to wrap MCP tools into an agent, and relies on Azure GPT-5 Nano for orchestrating tool calls. However, the workflow and actions are tailored to inventory tasks.

**Purpose**

While the store client prompts users to add or remove items from a basket, the warehouse client handles actions such as adding new products, removing existing ones, and viewing the entire inventory. It ensures that stock levels remain accurate and up to date.

#### How It Works:

The architecture mirrors the store client:
* Connection: It uses `MultiServerMCPClient` to connect to the warehouse MCP server running locally.
* Agent Setup: The tools exposed by the warehouse server (`get_products`, `check_product`, `update_quantity`, `add_product`, `remove_product`) are dynamically discovered and wrapped into a LangChain agent via `create_react_agent`.
* Guided Workflow: Like the store client, it does not parse free-form natural language. Instead, it prompts the user step by step:
    *   Choose an action: `add`, `remove`, `view`, or `exit`.
    *   If `add`: enter product name and quantity.
    *   If `remove`: enter product name and quantity.
    *   If `view`: display the current inventory.

This structured approach ensures clarity and prevents ambiguity.

**Example Interaction**

    Welcome to the Warehouse! Type 'exit' to quit.

    Add/remove/view/exit: add
    Item: mango
    Quantity: 20
    Added new product mango with quantity 20

    Add/remove/view/exit: view
    Current inventory:
    apple: 100
    banana: 50
    orange: 75
    grapes: 30
    mango: 20

Behind the scenes:
* The agent constructs a query like: 'Add 20 units of mango to the warehouse inventory'
* It maps this to the `add_product` MCP tool and sends a request to the warehouse server.
* The server responds with a confirmation message, which the client prints.

The warehouse client follows the same design principles as the store client but its domain is inventory management rather than basket operations.

<a name="Orchestrator"></a>
### The Orchestrator: MCP Client 

The orchestrator is where everything comes together. While the store and warehouse clients operate independently, the orchestrator coordinates both systems to maintain consistency between basket and stock. Its design follows the same principles as the previous clients: structured prompts, LangChain agent, and MCP integration—but introduces additional logic for validation and synchronisation.

#### Purpose
The orchestrator ensures that when a user adds an item to the basket, the warehouse has enough stock, and when an item is removed from the basket, the stock is replenished. This prevents overselling and keeps inventory accurate across both domains.

#### How It Works:

The setup is similar to the store and warehouse clients:
* Connection: Uses `MultiServerMCPClient` to connect to both MCP servers:
```python
{
    "mcpstore": {"url": "http://127.0.0.1:8001/mcp", "transport": "streamable_http"},
    "mcpwarehouse": {"url": "http://127.0.0.1:8002/mcp", "transport": "streamable_http"}
}
```
* Agent Setup: Discovers tools from both servers and wraps them into a single LangChain agent.
* Structured Workflow: Prompts the user for an action (`add`, `remove`, `view-basket`, `view-warehouse`) and then guides them through item and quantity inputs.

Where it differs:
* Validation Logic: Before adding to the basket, the orchestrator checks warehouse stock using `check_product`. If insufficient, it alerts the user.
* Stock Update: After a successful basket addition, it decrements warehouse stock. Similarly, when removing from the basket, it restores stock in the warehouse.

#### Helper Functions:
To support this logic, the orchestrator uses small utility functions:
* `extract_quantity(text)`: Parses numeric quantities from AI responses:

```python
def extract_quantity(text):
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0
```

* `extract_ai_message(response)`: Retrieves the content of AI messages for easier parsing.
* `extract_removed_quantity(response)`: Extracts item and quantity details from removal confirmations.

These helpers keep the main workflow clean and focused.

**Example End-to-End Flow**

    Welcome! Type 'exit' to quit.

    Choose action (add/remove/view-basket/view-warehouse): add
    Item: apple
    Quantity: 5

    Added apple with quantity: 5

Behind the scenes:
1.  The orchestrator queries the warehouse server via MCP to check stock.
2.  Validates that 5 units are available.
3.  Calls `add_item` on the store server to update the basket.
4.  Calls `update_quantity` on the warehouse server to decrement stock.
5.  Prints confirmation messages for each step.

The orchestrator combines the structured prompt model of the previous clients with additional business logic for validation and synchronisation. It ensures that basket operations and warehouse inventory remain in sync.

#### Watch It in Action
Here’s a quick demo of the multi-agent system adding and removing items from the basket while updating warehouse inventory in real time:
![demo](./docs/Demo.gif)

## Why This Architecture Works?

This architecture succeeds because it combines clear separation of concerns, protocol-driven interoperability, and structured user interaction with AI-powered orchestration. Here’s why it’s effective:

#### Modular Design
Each component has a single responsibility:
* Store Server manages basket operations.
* Warehouse Server manages stock.
* Clients provide user interfaces.
* Orchestrator enforces business rules and synchronisation.
This modularity makes the system easy to maintain, extend, and scale. Adding a new domain (e.g., shipping) would simply mean creating another MCP server and updating the orchestrator.

#### Standardised Communication via MCP
By using Model Context Protocol, all servers expose their functionality through a consistent interface. This eliminates the need for custom APIs and hardcoded integrations.

#### Structured Interaction
Instead of relying on ambiguous natural language, the system uses guided prompts for user input. This reduces errors, simplifies validation, and makes the workflow deterministic.

#### AI-Powered Orchestration
LangChain agents and Azure GPT-5 Nano provide reasoning capabilities without taking over the entire workflow. The LLM doesn’t guess user intent; it focuses on mapping structured queries to MCP tools and coordinating multi-step processes. This balance ensures reliability while leveraging AI for orchestration.

#### Data Consistency
The orchestrator enforces business logic:
* Validates stock before adding to the basket.
* Updates warehouse quantities after basket changes.

This prevents overselling and keeps both systems in sync—something that standalone clients cannot guarantee.

#### Scalability and Extensibility
Because the architecture is protocol-driven and modular:
* You can add new tools to servers without changing client logic.
* You can integrate additional MCP servers into the orchestrator with minimal effort.
* Persistent storage or authentication can be layered in without breaking the core design.

This architecture works because it combines clarity, consistency and composability, all under a standard protocol that plays well with AI orchestration. It’s simple enough for local deployments yet robust enough to scale into business workflows.

---
<a name="FutureEnhancements"></a>
## Future Enhancements
While the current implementation demonstrates a functional multi-agent inventory system, there are several opportunities to extend and refine it. These enhancements are not mandatory but serve as starting points for readers who want to build on this foundation.

* **Delegate Basket Operations to Orchestrator**  
    Simplify `store_client.py` by routing add/remove logic through `mcp_client.py` to avoid duplication and reduce maintenance overhead.

* **Chatbot Interface**  
    Replace structured prompts with a conversational interface that interprets natural language commands for a more intuitive user experience.

* **Authentication and Access Control**  
    Secure MCP servers with API keys or OAuth and implement role-based permissions to prevent unauthorised access.

* **Enhanced Quantity Parsing**  
    Improve helper functions to handle words like `ten` or phrases like `half a dozen` and validate against invalid quantities.

* **Error Handling**  
    Add robust error handling for invalid tool calls.

* **Observability and Logging**  
    Implement structured logging and monitoring to track tool calls, inventory changes, and system performance.

---
<a name="Conclusion"></a>
## Conclusion

This project illustrates how MCP combined with LangChain and FastMCP can turn a simple inventory workflow into a modular, AI-assisted system. By splitting responsibilities across MCP servers for the store and warehouse and coordinating them through an orchestrator, we achieve:
* Modularity: Each component focuses on a single responsibility, making the system easier to maintain and extend.
* Standardisation: MCP provides a consistent protocol for exposing tools and handling communication, eliminating the need for custom APIs.
* Structured Interaction with AI Orchestration: Guided prompts ensure reliability, while LangChain agents handle tool invocation.
* Data Consistency: The orchestrator enforces business rules, preventing overselling and keeping inventory accurate.

**Your Next Step:** Experiment and extend. Whether you want to add persistent storage, build a chatbot like interface, or containerise the system for deployment, MCP + LangChain + FastMCP gives you the foundation to do it. The scripts in this article can be a starting point so pick them up, adapt them, and create your own intelligent, multi-agent workflows!

---
<a name="Ressources"></a>
## Ressources
Here are the key references and materials that informed and supported this project:

* **Starting Point for Scripts**  
    [Building a Remote MCP Server and Client with FastMCP, LangChain, and LangGraph](https://medium.com/@anoopninangeorge/building-a-remote-mcp-server-a-mcp-client-with-fastmcp-langchain-langgraph-17cf0e8d043b)

  This Medium article served as the foundation for the scripts in this project. I reused and extended the concepts demonstrated there to build a multi-agent architecture with additional orchestration logic.

* **Model Context Protocol Documentation**
    *   [Getting Started](https://modelcontextprotocol.io/docs/getting-started/intro)
    *   [Architecture Overview](https://modelcontextprotocol.io/docs/learn/architecture)
    *   [Server Concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)
    *   [Client Concepts](https://modelcontextprotocol.io/docs/learn/client-concepts)

* **FastMCP Documentation**
    *   <https://gofastmcp.com/getting-started/welcome>
    *   <https://gofastmcp.com/servers/server>

These resources provide deeper insights into MCP fundamentals, FastMCP implementation details, and best practices for building AI-integrated systems. They are highly recommended for anyone looking to extend or customise the architecture presented in this article.




