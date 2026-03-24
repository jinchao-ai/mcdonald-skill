# 麦当劳 MCP API 参考文档（已修正，与实际接口一致）
## 目录
- [认证](#认证)
- [接口调用规范](#接口调用规范)
- [点餐功能](#点餐功能)
- [麦麦日历](#麦麦日历)
- [麦麦省领券](#麦麦省领券)
- [麦麦商城](#麦麦商城)
- [通用工具](#通用工具)
- [错误码说明](#错误码说明)

## 认证
**接入地址**: `https://mcp.mcd.cn`
**传输协议**: Streamable HTTP
**认证方式**: Bearer Token
请求头格式：
```
Authorization: Bearer YOUR_MCP_TOKEN
```

## 接口调用规范
所有接口统一通过`tools/call`方法调用：
```json
{
  "method": "tools/call",
  "params": {
    "name": "工具名称",
    "arguments": {
      // 接口参数
    }
  }
}
```

---

## 点餐功能
### 1. 餐品营养信息列表 (list-nutrition-foods)
查询所有餐品的营养信息
**入参**: 无
**响应示例**:
```json
{
  "success": true,
  "result": {
    "structuredContent": {
      "success": true,
      "data": [
        {
          "productCode": "123",
          "name": "麦辣鸡腿汉堡",
          "calories": "563",
          "protein": "26g",
          "fat": "33g"
        }
      ]
    }
  }
}
```

### 2. 获取用户可配送地址列表 (delivery-query-addresses)
查询用户保存的配送地址
**入参**: 无
**响应示例**:
```json
{
  "success": true,
  "result": {
    "structuredContent": {
      "success": true,
      "data": [
        {
          "addressId": "1036420330166781061022499154",
          "address": "北京市朝阳区望京东路6号望京国际研发园",
          "addressDetail": "I座2层",
          "contact": "许金超",
          "phone": "188****7651",
          "storeCode": "1950711",
          "beCode": "195071102",
          "isDefault": true
        }
      ]
    }
  }
}
```

### 3. 新增配送地址 (delivery-create-address)
为用户添加新的配送地址
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| province | string | 是 | 省份 |
| city | string | 是 | 城市 |
| district | string | 是 | 区县 |
| address | string | 是 | 大地址（街道/园区等） |
| addressDetail | string | 否 | 详细地址（门牌号/楼层/房间号） |
| contact | string | 是 | 联系人 |
| phone | string | 是 | 联系电话 |
| isDefault | boolean | 否 | 是否设为默认地址，默认false |

### 4. 查询用户在当前门店可用券 (query-store-coupons)
查询用户在指定门店可以使用的优惠券
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| storeCode | string | 是 | 门店编码（从地址查询结果获取） |
| beCode | string | 是 | 门店BE编码（从地址查询结果获取） |

### 5. 查询当前门店可售卖的餐品列表 (query-meals)
查询指定门店当前可售卖的餐品
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| storeCode | string | 是 | 门店编码 |
| beCode | string | 是 | 门店BE编码 |
| deliveryType | string | 否 | 配送类型：DELIVERY(外送)/PICKUP(到店取餐)，默认DELIVERY |

### 6. 查询餐品详情 (query-meal-detail)
查询指定餐品的详细信息
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| productCode | string | 是 | 商品编码 |
| storeCode | string | 是 | 门店编码 |
| beCode | string | 是 | 门店BE编码 |

### 7. 商品价格计算 (calculate-price)
计算订单的总价格（含优惠券折扣）
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| storeCode | string | 是 | 门店编码 |
| beCode | string | 是 | 门店BE编码 |
| items | array | 是 | 商品列表，格式：`[{"productCode": "xxx", "quantity": 1}]` |
| couponId | string | 否 | 优惠券ID |

### 8. 创建外送订单 (create-delivery-order)
创建麦乐送外送订单
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| addressId | string | 是 | 配送地址ID |
| storeCode | string | 是 | 门店编码 |
| beCode | string | 是 | 门店BE编码 |
| items | array | 是 | 商品列表，格式：`[{"productCode": "xxx", "quantity": 1}]` |
| couponId | string | 否 | 优惠券ID |
| remark | string | 否 | 订单备注 |

### 9. 查询订单详情 (query-order)
查询订单的详细信息和状态
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| orderId | string | 是 | 订单ID |

---

## 麦麦日历
### 活动日历查询工具 (calendar-query)
查询麦当劳的活动日历信息
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| year | number | 否 | 年份，默认当前年 |
| month | number | 否 | 月份，默认当前月 |

---

## 麦麦省领券
### 1. 可领取优惠券列表 (coupon-available-list)
查询当前可领取的优惠券列表
**入参**: 无

### 2. 领取优惠券 (claim-coupon)
领取指定的优惠券
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| couponId | string | 是 | 优惠券ID |

### 3. 我的优惠券查询 (coupon-my-list)
查询用户已领取的优惠券
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 券状态：AVAILABLE(可用)/USED(已使用)/EXPIRED(已过期)，默认查询全部 |

---

## 麦麦商城
### 1. 我的积分查询 (points-my-balance)
查询用户当前的积分余额
**入参**: 无

### 2. 积分兑换商品列表 (points-product-list)
查询可用积分兑换的商品列表
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| category | string | 否 | 商品分类 |

### 3. 积分兑换商品详情 (points-product-detail)
查询积分兑换商品的详细信息
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| productId | string | 是 | 积分商品ID |

### 4. 积分兑换商品下单 (points-exchange)
使用积分兑换商品
**入参**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| productId | string | 是 | 积分商品ID |
| quantity | number | 否 | 兑换数量，默认1 |

---

## 通用工具
### 当前时间信息查询工具 (current-time)
获取当前的服务器时间信息
**入参**: 无

---

## 错误码说明
| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权，Token 无效或过期 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 1001 | 门店不存在或当前地址不可配送 |
| 1002 | 商品不存在或已下架 |
| 1003 | 优惠券不可用/已过期 |
| 1004 | 积分不足 |
| 1005 | 商品库存不足 |
| 1006 | 存在待支付订单，请先完成支付或取消 |
