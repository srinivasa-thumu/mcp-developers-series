"""A tiny customer lookup MCP server using the official MCP Python SDK."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Customer Management MCP Server")

CUSTOMERS: dict[int, dict[str, str]] = {
    101: {"name": "John", "email": "john@example.com", "city": "Hyderabad"},
    102: {"name": "Sarah", "email": "sarah@example.com", "city": "Bangalore"},
    103: {"name": "David", "email": "david@example.com", "city": "Chennai"},
}


def find_customer(customer_id: int) -> dict[str, str]:
    """Return one customer's details, or raise a clear error when it is missing."""
    if not isinstance(customer_id, int) or isinstance(customer_id, bool):
        raise ValueError("customer_id must be an integer.")
    if customer_id <= 0:
        raise ValueError("customer_id must be a positive integer.")

    customer = CUSTOMERS.get(customer_id)
    if customer is None:
        raise ValueError(f"Customer with ID {customer_id} was not found.")

    return customer


@mcp.tool()
def get_customer(customer_id: int) -> dict[str, str]:
    """Look up a customer by ID and return their name, email, and city."""
    return find_customer(customer_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
