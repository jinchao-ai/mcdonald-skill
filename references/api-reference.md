# 麦当劳 MCP API 参考文档

## 目录

- [认证](#认证)
- [点餐功能](#点餐功能)
- [麦麦日历](#麦麦日历)
- [麦麦省领券](#麦麦省领券)
- [麦麦商城](#麦麦商城)
- [通用工具](#通用工具)

## 认证

**接入地址**: `https://mcp.mcd.cn`

**传输协议**: Streamable HTTP

**认证方式**: Bearer Token

请求头格式：
```
Authorization: Bearer YOUR_MCP_TOKEN
```

## 点餐功能

### 1. 餐品营养信息列表 (mcd_nutrition_list)

查询所有餐品的营养信息。

**入参**: 无

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "productId": "123",
      "productName": "xxxx",
      "calories": "563",
      "protein": "26g",
      "fat": "33g"
    }
  ]
}
```

### 2. 获取用户可配送地址列表 (mcd_delivery_address_list)

查询用户保存的配送地址。

**入参**: 无

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "addressId": "xxxx",
      "address": "xxxx朝阳区xxx",
      "contact": "xxxx",
      "phone": "xxxx"
    }
  ]
}
```

### 3. 新增配送地址 (mcd_add_delivery_address)

为用户添加新的配送地址。

**入参**:
- `province` (string, 必填): 省份
- `city` (string, 必填): 城市
- `district` (string, 必填): 区县
- `address` (string, 必填): 详细地址
- `contact` (string, 必填): 联系人
- `phone` (string, 必填): 联系电话
- `isDefault` (boolean, 可选): 是否设为默认地址

### 4. 查询用户在当前门店可用券 (mcd_store_available_coupons)

查询用户在指定门店可以使用的优惠券。

**入参**:
- `storeId` (string, 必填): 门店ID

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "couponId": "xxxx",
      "couponName": "xxxx",
      "discount": "5",
      "minAmount": "30",
      "expireTime": "2026-03-31"
    }
  ]
}
```

### 5. 查询当前门店可售卖的餐品列表 (mcd_store_product_list)

查询指定门店当前可售卖的餐品。

**入参**:
- `storeId` (string, 必填): 门店ID
- `deliveryType` (string, 可选): 配送类型 (DELIVERY/PICKUP)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "productId": "xxxx",
      "productName": "xxxx",
      "price": "23.5",
      "available": true,
      "category": "汉堡"
    }
  ]
}
```

### 6. 查询餐品详情 (mcd_product_detail)

查询指定餐品的详细信息。

**入参**:
- `productId` (string, 必填): 餐品ID
- `storeId` (string, 必填): 门店ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "productId": "xxxx",
    "productName": "xxxx",
    "price": "23.5",
    "description": "经典xxxx汉堡",
    "image": "https://...",
    "nutrition": {
      "calories": "563",
      "protein": "26g"
    }
  }
}
```

### 7. 商品价格计算 (mcd_calculate_price)

计算订单的总价格（含优惠券折扣）。

**入参**:
- `storeId` (string, 必填): 门店ID
- `products` (array, 必填): 商品列表
  - `productId` (string): 商品ID
  - `quantity` (number): 数量
- `couponId` (string, 可选): 优惠券ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "originalPrice": "50.0",
    "discount": "5.0",
    "finalPrice": "45.0"
  }
}
```

### 8. 创建外送订单 (mcd_create_delivery_order)

创建麦乐送外送订单。

**入参**:
- `storeId` (string, 必填): 门店ID
- `addressId` (string, 必填): 配送地址ID
- `products` (array, 必填): 商品列表
  - `productId` (string): 商品ID
  - `quantity` (number): 数量
- `couponId` (string, 可选): 优惠券ID
- `remark` (string, 可选): 订单备注

**响应示例**:
```json
{
  "success": true,
  "data": {
    "orderId": "xxxx",
    "orderNo": "xxxx",
    "totalPrice": "45.0",
    "status": "PENDING"
  }
}
```

### 9. 查询订单详情 (mcd_order_detail)

查询订单的详细信息和状态。

**入参**:
- `orderId` (string, 必填): 订单ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "orderId": "xxxx",
    "orderNo": "xxxx",
    "status": "DELIVERING",
    "products": [...],
    "totalPrice": "45.0",
    "deliveryAddress": "xxxx",
    "createTime": "2026-03-09 12:00:00"
  }
}
```

## 麦麦日历

### 活动日历查询工具 (mcd_calendar_query)

查询麦当劳的活动日历信息。

**入参**:
- `year` (number, 可选): 年份
- `month` (number, 可选): 月份

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2026-03-15",
      "title": "周三会员日",
      "description": "会员专享优惠",
      "type": "MEMBER_DAY"
    }
  ]
}
```

## 麦麦省领券

### 1. 麦麦省券列表查询 (mcd_coupon_list)

查询当前可领取的优惠券列表。

**入参**: 无

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "couponId": "xxxx",
      "couponName": "xxxx",
      "discount": "5",
      "minAmount": "30",
      "stock": 1000,
      "expireTime": "2026-03-31"
    }
  ]
}
```

### 2. 麦麦省一键领券 (mcd_claim_coupon)

领取指定的优惠券。

**入参**:
- `couponId` (string, 必填): 优惠券ID

**响应示例**:
```json
{
  "success": true,
  "message": "领取成功",
  "data": {
    "userCouponId": "xxxx",
    "expireTime": "2026-03-31"
  }
}
```

### 3. 我的优惠券查询 (mcd_my_coupons)

查询用户已领取的优惠券。

**入参**:
- `status` (string, 可选): 券状态 (AVAILABLE/USED/EXPIRED)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "userCouponId": "xxxx",
      "couponName": "xxxx",
      "status": "AVAILABLE",
      "expireTime": "2026-03-31"
    }
  ]
}
```

## 麦麦商城

### 1. 我的积分查询 (mcd_my_points)

查询用户当前的积分余额。

**入参**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "totalPoints": 1500,
    "availablePoints": 1200,
    "frozenPoints": 300
  }
}
```

### 2. 积分兑换商品列表 (mcd_points_product_list)

查询可用积分兑换的商品列表。

**入参**:
- `category` (string, 可选): 商品分类

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "productId": "points_xxxx",
      "productName": "xxxx",
      "pointsRequired": 500,
      "stock": 100,
      "image": "https://..."
    }
  ]
}
```

### 3. 积分兑换商品详情 (mcd_points_product_detail)

查询积分兑换商品的详细信息。

**入参**:
- `productId` (string, 必填): 商品ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "productId": "points_xxxx",
    "productName": "xxxx",
    "pointsRequired": 500,
    "description": "可兑换一份xxxx",
    "stock": 100,
    "validDays": 30
  }
}
```

### 4. 积分兑换商品下单 (mcd_points_exchange)

使用积分兑换商品。

**入参**:
- `productId` (string, 必填): 商品ID
- `quantity` (number, 可选): 兑换数量，默认为1

**响应示例**:
```json
{
  "success": true,
  "message": "兑换成功",
  "data": {
    "exchangeId": "xxxx",
    "pointsUsed": 500,
    "remainingPoints": 700
  }
}
```

## 通用工具

### 当前时间信息查询工具 (mcd_current_time)

获取当前的时间信息（服务器时间）。

**入参**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "timestamp": 1765447025424,
    "datetime": "2026-03-09T12:00:00.000",
    "formatted": "2026-03-09 12:00:00",
    "date": "2026-03-09",
    "year": 2026,
    "month": 3,
    "day": 9,
    "dayOfWeek": "MONDAY",
    "timezone": "GMT+08:00"
  }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权，Token 无效或过期 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 1001 | 门店不存在或不可用 |
| 1002 | 商品不存在或已下架 |
| 1003 | 优惠券不可用 |
| 1004 | 积分不足 |
| 1005 | 库存不足 |
