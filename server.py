"""Magento MCP server for Claude Desktop / Claude Code."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from magento_client import MagentoAPIError, MagentoClient, MagentoConfigError

mcp = FastMCP("Magento Manager")


def _client() -> MagentoClient:
    return MagentoClient()


def _error(exc: Exception) -> str:
    if isinstance(exc, MagentoConfigError):
        return f"Config error: {exc}"
    if isinstance(exc, MagentoAPIError):
        return f"API error {exc.status_code}: {exc.body}"
    return f"Unexpected error: {exc}"


# --- Products ---


@mcp.tool()
async def list_products(limit: int = 5, search: str | None = None) -> str:
    """List products from the Magento store. Optionally filter by name search."""
    try:
        data = await _client().list_products(page_size=limit, search=search)
        items = data.get("items", [])
        if not items:
            return "No products found."
        lines = [
            f"SKU: {item.get('sku')} | Name: {item.get('name')} | Price: {item.get('price', 'N/A')}"
            for item in items
        ]
        total = data.get("total_count", len(items))
        return f"Showing {len(items)} of {total} products:\n" + "\n".join(lines)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def get_product(sku: str) -> dict | str:
    """Get full details for a specific product SKU."""
    try:
        return await _client().get_product(sku)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def create_product(sku: str, name: str, price: float) -> str:
    """Create a new simple product in Magento."""
    try:
        product = await _client().create_product(sku=sku, name=name, price=price)
        return f"Created product: {product.get('name')} (SKU: {product.get('sku')})"
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def update_product_price(sku: str, new_price: float) -> str:
    """Update the price of an existing product."""
    try:
        product = await _client().update_product(sku, {"price": new_price})
        return f"Updated SKU {sku} to price {product.get('price', new_price)}"
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def update_product_name(sku: str, new_name: str) -> str:
    """Update the name of an existing product."""
    try:
        product = await _client().update_product(sku, {"name": new_name})
        return f"Updated SKU {sku} name to: {product.get('name', new_name)}"
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def update_product(
    sku: str,
    name: str | None = None,
    price: float | None = None,
) -> str:
    """Update product fields (name and/or price). Pass only the fields you want to change."""
    fields: dict = {}
    if name is not None:
        fields["name"] = name
    if price is not None:
        fields["price"] = price
    if not fields:
        return "Nothing to update. Provide name and/or price."
    try:
        product = await _client().update_product(sku, fields)
        return (
            f"Updated SKU {sku}: "
            f"name={product.get('name')} | price={product.get('price')}"
        )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def delete_product(sku: str) -> str:
    """Delete a product from Magento by SKU."""
    try:
        result = await _client().delete_product(sku)
        if result is True:
            return f"Deleted product with SKU: {sku}"
        return f"Delete response: {result}"
    except Exception as exc:
        return _error(exc)


# --- Orders ---


@mcp.tool()
async def list_orders(limit: int = 5, status: str | None = None) -> str:
    """List recent Magento orders. Optional status filter (e.g. pending, processing, complete)."""
    try:
        data = await _client().list_orders(page_size=limit, status=status)
        items = data.get("items", [])
        if not items:
            return "No orders found."
        lines = []
        for order in items:
            lines.append(
                " | ".join(
                    [
                        f"ID: {order.get('entity_id')}",
                        f"Increment: {order.get('increment_id')}",
                        f"Status: {order.get('status')}",
                        f"Grand total: {order.get('grand_total')}",
                        f"Customer: {order.get('customer_email', 'guest')}",
                    ]
                )
            )
        total = data.get("total_count", len(items))
        return f"Showing {len(items)} of {total} orders:\n" + "\n".join(lines)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def get_order(order_id: int) -> dict | str:
    """Get full details for a Magento order by entity ID."""
    try:
        return await _client().get_order(order_id)
    except Exception as exc:
        return _error(exc)


# --- Customers ---


@mcp.tool()
async def list_customers(limit: int = 5) -> str:
    """List customers from the Magento store."""
    try:
        data = await _client().list_customers(page_size=limit)
        items = data.get("items", [])
        if not items:
            return "No customers found."
        lines = [
            f"ID: {c.get('id')} | {c.get('firstname')} {c.get('lastname')} | {c.get('email')}"
            for c in items
        ]
        total = data.get("total_count", len(items))
        return f"Showing {len(items)} of {total} customers:\n" + "\n".join(lines)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def get_customer(customer_id: int) -> dict | str:
    """Get full details for a Magento customer by ID."""
    try:
        return await _client().get_customer(customer_id)
    except Exception as exc:
        return _error(exc)


# --- Categories ---


@mcp.tool()
async def list_categories() -> dict | str:
    """Get the Magento category tree."""
    try:
        return await _client().list_categories()
    except Exception as exc:
        return _error(exc)


if __name__ == "__main__":
    mcp.run()
