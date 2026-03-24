---
name: mcdonald-mcp
description: "McDonald's China MCP integration for ordering food, managing coupons, checking points, and accessing McDonald's services. Use when users ask to: (1) Order McDonald's food or check menu items, (2) Query or claim McDonald's coupons, (3) Check McDonald's points or redeem rewards, (4) View McDonald's calendar events, (5) Manage delivery addresses, (6) Check order status, or any McDonald's-related tasks."
---

# McDonald's MCP Integration

Integrate with McDonald's China MCP platform to access ordering, coupons, points, and other services.

## ⚠️ 首次使用提示

首次调用时会自动检查Token，未配置时会给出配置提示（附获取链接和配置命令）。

## Core Capabilities

### ⚠️ 全局规则（强制执行）
所有内部编码类字段（包括门店编码storeCode、BE编码beCode、餐品编码productCode、地址ID addressId、优惠券ID couponId等）为系统内部使用字段，**绝对禁止暴露给用户**。用户交互全程仅使用自然语言名称、序号即可，所有编码匹配由系统内部自动完成。

### 1. Food Ordering

> ⚡️ **点餐流程最佳实践（强制遵循）**
> - 用户说"点麦当劳"或类似需求时，**直接执行 `init_order`**
> - **不需要**单独查询token、不需要单独查地址，直接一次搞定
> - Python脚本内部会自动读取 `MCD_MCP_TOKEN`（从环境变量或 `$HOME/.openclaw/.env`），无需人工确认

#### 📋 完整CLI命令参考（全流程无需写Python代码）
| 命令 | 功能说明 | 用法示例 |
| --- | --- | --- |
| `init_order` | ⚡️ 初始化点餐上下文（地址+商品一次获取） | `python scripts/mcp_client.py init_order` |
| `delivery_addresses` | 获取已保存的配送地址列表 | `python scripts/mcp_client.py delivery_addresses` |
| `add_address` | 添加新配送地址 | `python scripts/mcp_client.py add_address 北京市 北京市 朝阳区 望京东路6号望京国际研发园 张三 13800138000 1` |
| `query_meals` | 查询门店可售餐品列表 | `python scripts/mcp_client.py query_meals <store_code> <be_code>` |
| `search_meal` | 按名称搜索商品 | `python scripts/mcp_client.py search_meal <store_code> <be_code> "麦乐鸡"` |
| `meal_detail` | 查询餐品详情/营养信息 | `python scripts/mcp_client.py meal_detail <product_code> <store_code> <be_code>` |
| `store_coupons` | 查询门店可用优惠券 | `python scripts/mcp_client.py store_coupons <store_code> <be_code>` |
| `claim_all_coupons` | 一键领取所有可领优惠券 | `python scripts/mcp_client.py claim_all_coupons` |
| `claim_coupon` | 领取指定优惠券 | `python scripts/mcp_client.py claim_coupon <coupon_id>` |
| `calculate_price` | 计算订单价格 | `python scripts/mcp_client.py calculate_price <store_code> <be_code> "麦辣鸡腿堡 1, 中薯条 2"` |
| `create_order` | 创建订单并自动打开支付页 | `python scripts/mcp_client.py create_order <address_id> <store_code> <be_code> "麦辣鸡腿堡 1, 中薯条 2"` |
| `query_order` | 查询订单详情/状态 | `python scripts/mcp_client.py query_order <订单号>` |
| `monitor_order` | 后台监控订单状态变化 | `python scripts/mcp_client.py monitor_order <订单号> [间隔分钟]` |
| `nutrition_list` | 获取餐品营养信息列表 | `python scripts/mcp_client.py nutrition_list` |

**自动订单状态监控（新功能）**
✅ 订单创建成功后**自动启动后台监控**，无需手动操作：
- 每5分钟自动查询一次订单状态
- 状态变化时主动发消息通知（待支付→制作中→配送中→已完成/已取消）
- 配送中会展示配送员姓名、电话、预计送达时间
- 订单完成/取消后自动停止监控

#### Complete Delivery Order Workflow（简化版）

**Step 1: 初始化点餐上下文（1次调用）**
```bash
python scripts/mcp_client.py init_order
```
返回：
- 地址列表（含 addressId, storeCode, beCode）
- 门店商品列表

**Step 2: 用户选餐**
用户选择商品后，直接创建订单：

```bash
python scripts/mcp_client.py create_order <address_id> <store_code> <be_code> "商品列表"
```

示例：
```bash
python scripts/mcp_client.py create_order 1036420330166781061022499154 1950711 195071102 "猪柳蛋麦满分套餐 1, 脆薯饼 1"
```

> ⚠️ **重要提醒**：
> - `create_order` 会自动领取优惠券、自动选择最优券、自动打开支付页
> - 无需手动执行 `coupon_list`、`claim_all_coupons`、`query_meals` 等命令
```
=== 麦当劳门店可点商品列表 ===
1. 爆脆精选单人餐 | 价格: ¥39.9 | 标签: 人气爆款、超值
2. 精选单人餐四件套 | 价格: ¥45.9 | 标签: 7.1折
3. 麦辣鸡腿汉堡中套餐 | 价格: ¥43 | 标签: -
```
⚠️ 注意：query-meals接口返回的`currentPrice`字段为**元为单位的字符串**，直接转float即可使用，不需要除以100。
用户只需要报序号或者商品名称即可，比如：
- "我要1号和3号"
- "我要一份麦乐鸡和一份脆汁鸡"
- "1号 2份，麦乐鸡 1份"
系统内部自动维护名称/序号与内部编码的映射关系，无需用户感知任何编码信息。

**Step 5: 自动解析用户输入并确认订单信息**
系统会自动识别用户输入的序号/名称，转换为对应商品编码，**在创建订单前必须向用户确认以下信息**：
- 配送地址（省市区+详细地址+联系人+电话）
- 商品清单（名称、数量、单价）
- 配送信息（预计送达时间、配送费等）
- 订单总金额

用户确认无误后再执行创建订单：
```python
from scripts.mcp_client import parse_order_items, create_order_and_pay

# 自动解析用户输入
items = parse_order_items(
    store_code='<门店编码>',
    be_code='<BE编码>',
    user_input='麦乐鸡 1, 脆汁鸡 1'
)

# ⚠️ 在此处向用户展示并确认订单信息，确认后再执行下面的创建订单操作

# 创建订单（默认自动领券+自动用最优优惠券）
result = create_order_and_pay(
    address_id='<地址ID>',
    store_code='<门店编码>',
    be_code='<BE编码>',
    items=items,
    auto_open_browser=True,
    auto_claim_coupons=True, # 自动领取所有可领优惠券，默认开启
    auto_use_coupon=True, # 自动使用优惠金额最大的优惠券，默认开启
    coupon_id=None # 手动指定优惠券ID，优先级最高
)
```

这个函数会自动完成：
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

**⚠️ 重要提示：**
- **订单15分钟内未支付会自动取消**，无需手动操作
- **本技能不支持取消订单操作**，如需取消已创建的订单，请在麦当劳手机App或小程序中手动取消

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
