---
name: mcdonald-mcp
description: "McDonald's China MCP integration for ordering food, managing coupons, checking points, and accessing McDonald's services. Use when users ask to: (1) Order McDonald's food or check menu items, (2) Query or claim McDonald's coupons, (3) Check McDonald's points or redeem rewards, (4) View McDonald's calendar events, (5) Manage delivery addresses, (6) Check order status, or any McDonald's-related tasks."
---

# McDonald's MCP Integration

Integrate with McDonald's China MCP platform to access ordering, coupons, points, and other services.

## Prerequisites

配置麦当劳MCP访问Token，支持两种方式（优先读取配置文件）：
1. **持久化配置（推荐）**：写入OpenClaw全局配置文件`~/.openclaw/.env`，永久生效：
```bash
echo "MCD_MCP_TOKEN=你的token值" >> ~/.openclaw/.env
```
2. **临时环境变量**：仅当前会话生效：
```bash
export MCD_MCP_TOKEN="your_token_here"
```

Get your token from: https://open.mcd.cn/mcp/doc

## Core Capabilities

### 1. Food Ordering

**自动订单状态监控（新功能）**
✅ 订单创建成功后**自动启动后台监控**，无需手动操作：
- 每5分钟自动查询一次订单状态
- 状态变化时主动发消息通知（待支付→制作中→配送中→已完成/已取消）
- 配送中会展示配送员姓名、电话、预计送达时间
- 订单完成/取消后自动停止监控

也可以手动监控任意订单：
```bash
# 监控指定订单，默认5分钟查询一次
python scripts/mcp_client.py monitor_order <订单号>
# 自定义查询间隔（比如3分钟查一次）
python scripts/mcp_client.py monitor_order <订单号> 3
```

**Check nutrition information:**
```bash
python scripts/mcp_client.py nutrition_list
```

#### Complete Delivery Order Workflow（优化版）

**Step 1: 检查待支付订单（自动执行，避免重复下单）**
创建订单前会自动查询是否有待支付订单，如有会提示用户确认是否继续创建新订单，避免重复扣费。

**Step 2: 查询并领取优惠券（可选）**
```bash
# 查询可领优惠券
python scripts/mcp_client.py coupon_list
# 一键领取所有优惠券
python scripts/mcp_client.py claim_all_coupons
```
领取的优惠券会在支付页自动展示，可以直接抵扣。

**Step 3: 添加或检查配送地址**
首先检查已有配送地址：
```python
from scripts.mcp_client import get_delivery_addresses
addresses = get_delivery_addresses()
```
如果没有地址，添加新地址：
```python
from scripts.mcp_client import add_delivery_address
result = add_delivery_address(
    province="北京市",
    city="北京市",
    district="朝阳区",
    address="望京东路6号望京国际研发园",
    addressDetail="I座2层",
    contact="许金超",
    phone="188****7651",
    is_default=True
)
# 保存返回的addressId, storeCode, beCode
```

**Step 4: 查询门店可售商品（用户无需关心编码）**
使用地址返回的storeCode和beCode查询商品，展示给用户的格式只有序号、名称、价格、标签，用户不需要记任何编码：
```
=== 麦当劳门店可点商品列表 ===
1. 【爆脆精选单人餐 | 价格: ¥39.9 | 标签: 人气爆款、超值
2. 【精选单人餐四件套 | 价格: ¥45.9 | 标签: 7.1折
3. 【麦辣鸡腿汉堡中套餐 | 价格: ¥43 | 标签: -
```
用户只需要报序号或者商品名称即可，比如：
- "我要1号和3号"
- "我要一份麦乐鸡和一份脆汁鸡"
- "1号 2份，麦乐鸡 1份"

**Step 5: 自动解析用户输入创建订单（无需手动填写编码）**
系统会自动识别用户输入的序号/名称，转换为对应商品编码创建订单：
```python
from scripts.mcp_client import parse_order_items, create_order_and_pay

# 自动解析用户输入
items = parse_order_items(
    store_code='1950711',
    be_code='195071102',
    user_input='麦乐鸡 1, 脆汁鸡 1'
)

# 创建订单（默认自动领券+自动用最优优惠券）
result = create_order_and_pay(
    address_id='1036420330166781061022499154',
    store_code='1950711',
    be_code='195071102',
    items=items,
    auto_open_browser=True,
    auto_claim_coupons=True, # 自动领取所有可领优惠券，默认开启
    auto_use_coupon=True, # 自动使用优惠金额最大的优惠券，默认开启
    coupon_id=None # 手动指定优惠券ID，优先级最高
)
```

这个函数会自动完成：
- ✅ 检查待支付订单，避免重复下单
- ✅ 自动领取所有可领优惠券（可配置）
- ✅ 自动查询当前门店可用优惠券，选择优惠金额最大的使用（可配置）
- ✅ 支持手动指定优惠券ID
- ✅ 创建订单时自动绑定优惠券，无需用户支付时手动勾选
- ✅ 优先使用OpenClaw内置浏览器打开支付页，直接展示可扫码的页面
- ✅  fallback到系统默认浏览器
- ✅ 打印订单号、金额、支付链接等信息

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
