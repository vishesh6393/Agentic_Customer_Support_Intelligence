import os

import httpx
from mcp.server.fastmcp import FastMCP

API = os.getenv("SUPPORT_API_URL", "http://localhost:8001")
mcp = FastMCP("support-tools")


@mcp.tool()
def get_orders(email: str) -> list:
    """List all orders of a customer by email."""
    return httpx.get(f"{API}/customers/{email}/orders").raise_for_status().json()


@mcp.tool()
def refund_order(order_id: int) -> dict:
    """Refund an order. Risky: needs human approval."""
    return httpx.post(f"{API}/orders/{order_id}/refund").raise_for_status().json()


@mcp.tool()
def create_ticket(customer_email: str, category: str, message: str) -> dict:
    """Open a support ticket. category: billing | tech | orders."""
    body = {"customer_email": customer_email, "category": category, "message": message}
    return httpx.post(f"{API}/tickets", json=body).raise_for_status().json()


@mcp.resource("policy://refunds")
def refund_policy() -> str:
    """Company refund policy."""
    return "Refunds allowed within 30 days of delivery. Refunds over 5000 need a manager."


@mcp.prompt()
def support_agent() -> str:
    return "You are a polite support agent. Always check orders before refunding."


if __name__ == "__main__":
    mcp.run()