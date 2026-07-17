"""Get a Magento admin API access token."""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

magento_url = os.getenv("MAGENTO_URL", "").rstrip("/")
username = os.getenv("MAGENTO_ADMIN_USERNAME", "")
password = os.getenv("MAGENTO_ADMIN_PASSWORD", "")

missing = [
    name
    for name, value in {
        "MAGENTO_URL": magento_url,
        "MAGENTO_ADMIN_USERNAME": username,
        "MAGENTO_ADMIN_PASSWORD": password,
    }.items()
    if not value
]
if missing:
    raise SystemExit(f"Missing required .env values: {', '.join(missing)}")

api_url = f"{magento_url}/integration/admin/token"

payload = {
    "username": username,
    "password": password,
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

try:
    response = httpx.post(
        api_url,
        json=payload,
        headers=headers,
        timeout=30.0,
        follow_redirects=True,
    )
except httpx.RequestError as exc:
    raise SystemExit(f"Request error: {exc}") from exc

if response.status_code == 200:
    token = response.json()
    print("Access Token:")
    print(token)
else:
    print("Authentication Failed")
    print(f"HTTP Code: {response.status_code}")
    print(f"Response:\n{response.text[:500]}")
    if "Just a moment" in response.text or "cloudflare" in response.text.lower():
        print(
            "\nHint: Cloudflare is blocking this request. "
            "Use your own Magento store URL (Cloudways), not the public demo."
        )
