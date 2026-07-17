# Magento MCP Server + Data Fetcher

Python tools to:
1. Fetch Magento store data from the CLI (`app.py`)
2. Expose Magento tools to Claude via MCP (`server.py`)

Both share the same REST client in `magento_client.py`.

## Setup

```bash
cd magento-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your store details:

```env
MAGENTO_URL=https://your-store.com/rest/V1
ACCESS_TOKEN=your_integration_access_token
```

### Magento Integration Token

1. Magento Admin → **System → Extensions → Integrations**
2. Add New Integration
3. API tab: set **Resource Access = All** (or at least Catalog → Products)
4. Activate and copy the **Access Token**
5. Put that token in `.env` as `ACCESS_TOKEN`
6. **Required on Magento 2.4.4+:**  
   Admin → **Stores → Configuration → Services → OAuth → Consumer Settings**  
   Set **Allow OAuth Access Tokens to be used as standalone Bearer tokens = Yes**  
   Then run: `php bin/magento cache:flush`

Without step 6, Magento returns:
`The consumer isn't authorized to access Magento_Catalog::products`
even when the integration has full API access.

## CLI data fetching

```bash
python app.py products --limit 10
python app.py products --search shirt
python app.py product WJ12
python app.py orders --limit 5 --status processing
python app.py order 12
python app.py customers
python app.py categories
```

Add `--json` on list commands for raw Magento JSON.

## MCP server for Claude Desktop

1. Install dependencies (see Setup above).
2. Open Claude Desktop config:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. Add the server (update the paths):

```json
{
  "mcpServers": {
    "magento": {
      "command": "C:\\Users\\Etech\\Desktop\\magento-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\Etech\\Desktop\\magento-mcp\\server.py"],
      "cwd": "C:\\Users\\Etech\\Desktop\\magento-mcp"
    }
  }
}
```

4. Restart Claude Desktop.
5. Ask Claude things like:
   - "List the latest Magento products"
   - "Show pending orders"
   - "Get product details for SKU WJ12"

### Available MCP tools

| Tool | Purpose |
|------|---------|
| `list_products` | List / search products |
| `get_product` | Product by SKU |
| `create_product` | Create simple product |
| `update_product_price` | Update price |
| `update_product_name` | Update product name |
| `update_product` | Update name and/or price |
| `delete_product` | Delete by SKU |
| `list_orders` | List / filter orders |
| `get_order` | Order by ID |
| `list_customers` | List customers |
| `get_customer` | Customer by ID |
| `list_categories` | Category tree |

## Project layout

```
magento-mcp/
  magento_client.py   # Shared Magento REST client
  server.py           # MCP server for Claude
  app.py              # CLI data fetcher
  .env                # Your secrets (do not commit)
  .env.example        # Template
  requirements.txt
```
