---
name: mcdonald-mcp
description: "McDonald's China MCP integration for ordering food, managing coupons, checking points, and accessing McDonald's services. Use when users ask to: (1) Order McDonald's food or check menu items, (2) Query or claim McDonald's coupons, (3) Check McDonald's points or redeem rewards, (4) View McDonald's calendar events, (5) Manage delivery addresses, (6) Check order status, or any McDonald's-related tasks."
---

# McDonald's MCP Integration

Integrate with McDonald's China MCP platform to access ordering, coupons, points, and other services.

## Prerequisites

Set the MCD_MCP_TOKEN environment variable with your McDonald's MCP token:

```bash
export MCD_MCP_TOKEN="your_token_here"
```

Get your token from: https://open.mcd.cn/mcp/doc

## Core Capabilities

### 1. Food Ordering

**Check nutrition information:**
```bash
python scripts/mcp_client.py nutrition_list
```

#### Complete Delivery Order Workflow

**Step 1: Add or Check Delivery Address**

First, check if you have delivery addresses:
```python
from scripts.mcp_client import get_delivery_addresses
addresses = get_delivery_addresses()
```

If no address exists, add one:
```python
import requests
import json

token = os.environ.get("MCD_MCP_TOKEN")
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

payload = {
    'method': 'tools/call',
    'params': {
        'name': 'delivery-create-address',
        'arguments': {
            'city': 'xxxx',
            'contactName': 'xxxx',
            'phone': 'xxxx',
            'address': 'xxxx',
            'addressDetail': 'xxxx'
        }
    }
}

response = requests.post('https://mcp.mcd.cn', headers=headers, json=payload)
result = response.json()
# Save addressId, storeCode, beCode from response
```

**Step 2: Query Store Products**

Use storeCode and beCode from address response:
```python
payload = {
    'method': 'tools/call',
    'params': {
        'name': 'query-meals',
        'arguments': {
            'storeCode': 'xxxx',
            'beCode': 'xxxx'
        }
    }
}
```

**Step 3: Calculate Price (Optional)**

Before creating order, calculate total price:
```python
payload = {
    'method': 'tools/call',
    'params': {
        'name': 'calculate-price',
        'arguments': {
            'storeCode': 'xxxx',
            'beCode': 'xxxx',
            'items': [
                {'productCode': 'xxxx', 'quantity': 1},
                {'productCode': 'xxxx', 'quantity': 1}
            ]
        }
    }
}
```

**Step 4: Create Order**

Create delivery order with addressId:
```python
payload = {
    'method': 'tools/call',
    'params': {
        'name': 'create-order',
        'arguments': {
            'addressId': 'xxxx',
            'storeCode': 'xxxx',
            'beCode': 'xxxx',
            'items': [
                {'productCode': 'xxxx', 'quantity': 1},
                {'productCode': 'xxxx', 'quantity': 1}
            ]
        }
    }
}
# Response includes orderId and payH5Url for payment
```

**Alternative: Create Order and Auto-Open Browser**

Use the helper function to create order and automatically open payment page:
```python
from scripts.mcp_client import create_order_and_pay

result = create_order_and_pay(
    address_id='xxxx',
    store_code='xxxx',
    be_code='xxxx',
    items=[
        {'productCode': 'xxxx', 'quantity': 1},
        {'productCode': 'xxxx', 'quantity': 1}
    ],
    auto_open_browser=True  # Automatically opens browser for payment
)
```

This function will:
- Create the order
- Print order details (order ID, total amount)
- Automatically open the payment URL in your default browser
- Display QR code page for scanning and payment

**Step 5: Payment**

After order creation, you'll receive:
- `orderId`: Order number for tracking
- `payH5Url`: Payment link (open in McDonald's App or browser)
- Order status: "待支付" (Pending Payment)

**Step 6: Check Order Status**

Query order status anytime:
```python
payload = {
    'method': 'tools/call',
    'params': {
        'name': 'query-order',
        'arguments': {
            'orderId': 'xxxx'
        }
    }
}
```

Order status progression:
- 待支付 (Pending Payment)
- 制作中 (Preparing)
- 配送中 (Delivering)
- 已完成 (Completed)

### 2. Coupon Management

**View available coupons:**
```bash
python scripts/mcp_client.py coupon_list
```

**Claim a coupon:**
```bash
python scripts/mcp_client.py claim_coupon <coupon_id>
```

**Check my coupons:**
```bash
python scripts/mcp_client.py my_coupons
```

Filter by status: AVAILABLE, USED, or EXPIRED

### 3. Points & Rewards

**Check points balance:**
```bash
python scripts/mcp_client.py my_points
```

**Browse redemption catalog:**
```bash
python scripts/mcp_client.py points_products
```

**Redeem with points:**
Use the Python client's `exchange_points_product()` function with product_id and quantity.

### 4. Calendar & Events

**View McDonald's calendar:**
```bash
python scripts/mcp_client.py calendar
```

Query specific month: provide year and month parameters.

### 5. Address Management

**List addresses:**
```bash
python scripts/mcp_client.py delivery_addresses
```

**Add new address:**
Use the Python client's `add_delivery_address()` function with province, city, district, address, contact, and phone.

## Using the Python Client

Import and use functions directly:

```python
from scripts.mcp_client import *

# Query products
products = get_store_products("xxxx")

# Claim coupon
result = claim_coupon("xxxx")

# Check points
points = get_my_points()
```

## API Reference

For detailed API documentation including all parameters, response formats, and error codes, see [references/api-reference.md](references/api-reference.md).

## Common Workflows

### Complete Delivery Order Example

**Scenario**: Order a xxxx and xxxx for delivery

```python
import requests
import json
import os

token = os.environ.get("MCD_MCP_TOKEN")
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
base_url = 'https://mcp.mcd.cn'

# Step 1: Add delivery address (if needed)
add_address = {
    'method': 'tools/call',
    'params': {
        'name': 'delivery-create-address',
        'arguments': {
            'city': 'xxxx',
            'contactName': 'xxxx',
            'phone': 'xxxx',
            'address': 'xxxx',
            'addressDetail': 'xxxx'
        }
    }
}
response = requests.post(base_url, headers=headers, json=add_address)
address_data = response.json()['result']['structuredContent']['data']
address_id = address_data['addressId']
xxxx = address_data['storeCode']
xxxx = address_data['beCode']

# Step 2: Query store products
query_meals = {
    'method': 'tools/call',
    'params': {
        'name': 'query-meals',
        'arguments': {
            'storeCode': xxxx,
            'beCode': xxxx
        }
    }
}
response = requests.post(base_url, headers=headers, json=query_meals)
meals = response.json()['result']['structuredContent']['data']['meals']
# Browse meals and select: xxxx (xxxx), xxxx (xxxx)

# Step 3: Calculate price
calc_price = {
    'method': 'tools/call',
    'params': {
        'name': 'calculate-price',
        'arguments': {
            'storeCode': xxxx,
            'beCode': xxxx,
            'items': [
                {'productCode': 'xxxx', 'quantity': 1},
                {'productCode': 'xxxx', 'quantity': 1}
            ]
        }
    }
}
response = requests.post(base_url, headers=headers, json=calc_price)
price_data = response.json()['result']['structuredContent']['data']
print(f"Total: ¥{price_data['price']/100}")

# Step 4: Create order
create_order = {
    'method': 'tools/call',
    'params': {
        'name': 'create-order',
        'arguments': {
            'addressId': address_id,
            'storeCode': xxxx,
            'beCode': xxxx,
            'items': [
                {'productCode': 'xxxx', 'quantity': 1},
                {'productCode': 'xxxx', 'quantity': 1}
            ]
        }
    }
}
response = requests.post(base_url, headers=headers, json=create_order)
order_data = response.json()['result']['structuredContent']['data']
order_id = order_data['orderId']
pay_url = order_data['payH5Url']

print(f"Order created: {order_id}")
print(f"Payment link: {pay_url}")

# Step 5: Check order status
query_order = {
    'method': 'tools/call',
    'params': {
        'name': 'query-order',
        'arguments': {
            'orderId': order_id
        }
    }
}
response = requests.post(base_url, headers=headers, json=query_order)
order_status = response.json()['result']['structuredContent']['data']
print(f"Order status: {order_status['orderStatus']}")
```

### Order with Coupon

**Redeem points:**
1. Check points balance
2. Browse redemption catalog
3. Select product and redeem

**Manage coupons:**
1. View available coupons
2. Claim desired coupons
3. Check my coupons before ordering
