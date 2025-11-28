from fastmcp import FastMCP

mcp = FastMCP("MCP_WAREHOUSE")

# Warehouse inventory
warehouse_inventory = {"apple": 100,
                       "banana": 50,
                       "orange": 75,
                       "grapes": 30,
                       "mango": 20,}

@mcp.tool()
def get_products() -> dict:
    """Get all products and their available quantities in the warehouse."""
    return {"products": warehouse_inventory}

@mcp.tool()
def check_product(key: str) -> str:
    """Check if a product exists and its available quantity."""
    if key in warehouse_inventory:
        return f"{key} available: {warehouse_inventory[key]}"
    return f"Product {key} not found in warehouse."

@mcp.tool()
def update_quantity(key: str, quantity: int) -> str:
    """Update the quantity of a product in the warehouse."""
    if key in warehouse_inventory:
        warehouse_inventory[key] = quantity
        return f"Updated {key} quantity to {quantity}"
    return f"Product {key} not found."

@mcp.tool()
def add_product(key: str, quantity: int) -> str:
    """Add a new product to the warehouse."""
    if key in warehouse_inventory:
        return f"Product {key} already exists with quantity {warehouse_inventory[key]}"
    warehouse_inventory[key] = quantity
    return f"Added new product {key} with quantity {quantity}"

@mcp.tool()
def remove_product(key: str) -> str:
    """Remove a product from the warehouse."""
    if key in warehouse_inventory:
        qty = warehouse_inventory.pop(key)
        return f"Removed {key} (quantity was {qty})"
    return f"Product {key} not found."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8002)