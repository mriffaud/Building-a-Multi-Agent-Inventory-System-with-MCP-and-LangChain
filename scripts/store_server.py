from fastmcp import FastMCP

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