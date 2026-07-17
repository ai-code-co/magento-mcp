"""CLI Magento data-fetching application.

Examples:
  python app.py products --limit 10
  python app.py products --search shirt
  python app.py product WJ12
  python app.py orders --limit 5 --status processing
  python app.py order 12
  python app.py customers
  python app.py categories
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from magento_client import MagentoAPIError, MagentoClient, MagentoConfigError


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, default=str))


async def cmd_products(args: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.list_products(
        page_size=args.limit,
        current_page=args.page,
        search=args.search,
    )
    if args.json:
        _print_json(data)
        return

    items = data.get("items", [])
    print(f"Products ({len(items)} of {data.get('total_count', len(items))}):")
    for item in items:
        print(
            f"  - {item.get('sku'):<20} {item.get('name'):<40} "
            f"price={item.get('price', 'N/A')}"
        )


async def cmd_product(args: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.get_product(args.sku)
    _print_json(data)


async def cmd_orders(args: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.list_orders(
        page_size=args.limit,
        current_page=args.page,
        status=args.status,
    )
    if args.json:
        _print_json(data)
        return

    items = data.get("items", [])
    print(f"Orders ({len(items)} of {data.get('total_count', len(items))}):")
    for order in items:
        print(
            f"  - #{order.get('increment_id')} "
            f"(id={order.get('entity_id')}) "
            f"status={order.get('status')} "
            f"total={order.get('grand_total')} "
            f"email={order.get('customer_email', 'guest')}"
        )


async def cmd_order(args: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.get_order(args.order_id)
    _print_json(data)


async def cmd_customers(args: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.list_customers(
        page_size=args.limit,
        current_page=args.page,
    )
    if args.json:
        _print_json(data)
        return

    items = data.get("items", [])
    print(f"Customers ({len(items)} of {data.get('total_count', len(items))}):")
    for customer in items:
        print(
            f"  - id={customer.get('id')} "
            f"{customer.get('firstname')} {customer.get('lastname')} "
            f"<{customer.get('email')}>"
        )


async def cmd_customer(args: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.get_customer(args.customer_id)
    _print_json(data)


async def cmd_categories(_: argparse.Namespace) -> None:
    client = MagentoClient()
    data = await client.list_categories()
    _print_json(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Magento store data via REST API",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    products = sub.add_parser("products", help="List products")
    products.add_argument("--limit", type=int, default=10)
    products.add_argument("--page", type=int, default=1)
    products.add_argument("--search", type=str, default=None)
    products.add_argument("--json", action="store_true")
    products.set_defaults(func=cmd_products)

    product = sub.add_parser("product", help="Get one product by SKU")
    product.add_argument("sku")
    product.set_defaults(func=cmd_product)

    orders = sub.add_parser("orders", help="List orders")
    orders.add_argument("--limit", type=int, default=10)
    orders.add_argument("--page", type=int, default=1)
    orders.add_argument("--status", type=str, default=None)
    orders.add_argument("--json", action="store_true")
    orders.set_defaults(func=cmd_orders)

    order = sub.add_parser("order", help="Get one order by entity ID")
    order.add_argument("order_id", type=int)
    order.set_defaults(func=cmd_order)

    customers = sub.add_parser("customers", help="List customers")
    customers.add_argument("--limit", type=int, default=10)
    customers.add_argument("--page", type=int, default=1)
    customers.add_argument("--json", action="store_true")
    customers.set_defaults(func=cmd_customers)

    customer = sub.add_parser("customer", help="Get one customer by ID")
    customer.add_argument("customer_id", type=int)
    customer.set_defaults(func=cmd_customer)

    categories = sub.add_parser("categories", help="Get category tree")
    categories.set_defaults(func=cmd_categories)

    return parser


async def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        await args.func(args)
        return 0
    except MagentoConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1
    except MagentoAPIError as exc:
        print(f"API error {exc.status_code}: {exc.body}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
