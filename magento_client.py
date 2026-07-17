"""Shared Magento 2 REST API client used by the MCP server and CLI app."""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

MAGENTO_URL = os.getenv("MAGENTO_URL", "").rstrip("/")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


class MagentoConfigError(RuntimeError):
    """Raised when Magento credentials or base URL are missing."""


class MagentoClient:
    """Thin async wrapper around Magento 2 REST endpoints."""

    def __init__(
        self,
        base_url: str | None = None,
        access_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or MAGENTO_URL).rstrip("/")
        self.access_token = access_token or ACCESS_TOKEN
        self.timeout = timeout

        if not self.base_url:
            raise MagentoConfigError(
                "MAGENTO_URL is not set. Example: https://your-store.com/rest/V1"
            )
        if not self.access_token:
            raise MagentoConfigError(
                "ACCESS_TOKEN is not set. Use a Magento Integration Access Token."
            )

    @property
    def headers(self) -> dict[str, str]:
        return {
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {self.access_token}",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=json,
            )

        if response.status_code >= 400:
            raise MagentoAPIError(response.status_code, response.text)

        if response.status_code == 204 or not response.content:
            return True

        return response.json()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, Any]) -> Any:
        return await self.request("POST", path, json=json)

    async def put(self, path: str, json: dict[str, Any]) -> Any:
        return await self.request("PUT", path, json=json)

    async def delete(self, path: str) -> Any:
        return await self.request("DELETE", path)

    # --- Products ---

    async def list_products(
        self,
        page_size: int = 10,
        current_page: int = 1,
        search: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "searchCriteria[pageSize]": page_size,
            "searchCriteria[currentPage]": current_page,
        }
        if search:
            params.update(
                {
                    "searchCriteria[filter_groups][0][filters][0][field]": "name",
                    "searchCriteria[filter_groups][0][filters][0][value]": f"%{search}%",
                    "searchCriteria[filter_groups][0][filters][0][condition_type]": "like",
                }
            )
        return await self.get("products", params=params)

    async def get_product(self, sku: str) -> dict[str, Any]:
        return await self.get(f"products/{sku}")

    async def create_product(
        self,
        sku: str,
        name: str,
        price: float,
        *,
        attribute_set_id: int = 4,
        status: int = 1,
        visibility: int = 4,
        type_id: str = "simple",
    ) -> dict[str, Any]:
        payload = {
            "product": {
                "sku": sku,
                "name": name,
                "price": price,
                "status": status,
                "visibility": visibility,
                "type_id": type_id,
                "attribute_set_id": attribute_set_id,
            }
        }
        return await self.post("products", json=payload)

    async def update_product(self, sku: str, fields: dict[str, Any]) -> dict[str, Any]:
        return await self.put(f"products/{sku}", json={"product": fields})

    async def delete_product(self, sku: str) -> Any:
        return await self.delete(f"products/{sku}")

    # --- Orders ---

    async def list_orders(
        self,
        page_size: int = 10,
        current_page: int = 1,
        status: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "searchCriteria[pageSize]": page_size,
            "searchCriteria[currentPage]": current_page,
        }
        if status:
            params.update(
                {
                    "searchCriteria[filter_groups][0][filters][0][field]": "status",
                    "searchCriteria[filter_groups][0][filters][0][value]": status,
                    "searchCriteria[filter_groups][0][filters][0][condition_type]": "eq",
                }
            )
        return await self.get("orders", params=params)

    async def get_order(self, order_id: int) -> dict[str, Any]:
        return await self.get(f"orders/{order_id}")

    # --- Customers ---

    async def list_customers(
        self,
        page_size: int = 10,
        current_page: int = 1,
    ) -> dict[str, Any]:
        params = {
            "searchCriteria[pageSize]": page_size,
            "searchCriteria[currentPage]": current_page,
        }
        return await self.get("customers/search", params=params)

    async def get_customer(self, customer_id: int) -> dict[str, Any]:
        return await self.get(f"customers/{customer_id}")

    # --- Categories ---

    async def list_categories(self) -> dict[str, Any]:
        return await self.get("categories")

    async def get_category(self, category_id: int) -> dict[str, Any]:
        return await self.get(f"categories/{category_id}")


class MagentoAPIError(RuntimeError):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"Magento API error {status_code}: {body}")
