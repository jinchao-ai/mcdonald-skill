#!/usr/bin/env python3
"""
麦当劳 MCP 客户端脚本
用于调用麦当劳 MCP API 的各种功能
"""

import os
import sys
import json
import requests
import webbrowser
from typing import Dict, Any, Optional, List

MCP_BASE_URL = "https://mcp.mcd.cn"

def get_token() -> str:
    """从环境变量获取 MCP Token"""
    token = os.environ.get("MCD_MCP_TOKEN")
    if not token:
        raise ValueError("请设置环境变量 MCD_MCP_TOKEN")
    return token

def call_mcp_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    调用 MCP 工具

    Args:
        tool_name: 工具名称
        arguments: 工具参数

    Returns:
        API 响应结果
    """
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }

    try:
        response = requests.post(MCP_BASE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }

# 点餐功能
def get_nutrition_list() -> Dict[str, Any]:
    """获取餐品营养信息列表"""
    return call_mcp_tool("list-nutrition-foods")

def get_delivery_addresses() -> Dict[str, Any]:
    """获取用户配送地址列表"""
    return call_mcp_tool("delivery-query-addresses")

def add_delivery_address(province: str, city: str, district: str,
                        address: str, contact: str, phone: str,
                        is_default: bool = False) -> Dict[str, Any]:
    """添加配送地址"""
    return call_mcp_tool("delivery-create-address", {
        "province": province,
        "city": city,
        "district": district,
        "address": address,
        "contact": contact,
        "phone": phone,
        "isDefault": is_default
    })

def get_store_coupons(store_code: str, be_code: str) -> Dict[str, Any]:
    """查询门店可用优惠券"""
    return call_mcp_tool("query-store-coupons", {
        "storeCode": store_code,
        "beCode": be_code
    })

def get_store_products(store_code: str, be_code: str) -> Dict[str, Any]:
    """查询门店可售餐品列表"""
    return call_mcp_tool("query-meals", {
        "storeCode": store_code,
        "beCode": be_code
    })

def get_product_detail(product_code: str, store_code: str, be_code: str) -> Dict[str, Any]:
    """查询餐品详情"""
    return call_mcp_tool("query-meal-detail", {
        "productCode": product_code,
        "storeCode": store_code,
        "beCode": be_code
    })

def calculate_price(store_code: str, be_code: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算订单价格"""
    return call_mcp_tool("calculate-price", {
        "storeCode": store_code,
        "beCode": be_code,
        "items": items
    })

def create_delivery_order(store_code: str, be_code: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """创建外送订单"""
    return call_mcp_tool("create-order", {
        "storeCode": store_code,
        "beCode": be_code,
        "items": items
    })

def create_order_and_pay(address_id: str, store_code: str, be_code: str,
                         items: List[Dict[str, Any]],
                         auto_open_browser: bool = True) -> Dict[str, Any]:
    """
    创建外送订单并自动打开支付链接

    Args:
        address_id: 配送地址ID
        store_code: 门店编码
        be_code: BE编码
        items: 商品列表
        auto_open_browser: 是否自动打开浏览器支付页面

    Returns:
        订单信息，包含 orderId 和 payH5Url
    """
    result = call_mcp_tool("create-order", {
        "addressId": address_id,
        "storeCode": store_code,
        "beCode": be_code,
        "items": items
    })

    # 检查是否成功创建订单
    if result.get("jsonrpc") == "2.0" and "result" in result:
        structured_content = result.get("result", {}).get("structuredContent", {})
        if structured_content.get("success") and "data" in structured_content:
            data = structured_content["data"]
            pay_url = data.get("payH5Url")
            order_id = data.get("orderId")

            print(f"✅ 订单创建成功！")
            print(f"📋 订单号: {order_id}")
            print(f"💰 总金额: ¥{data.get('orderDetail', {}).get('realTotalAmount', 'N/A')}")
            print(f"💳 支付链接: {pay_url}")

            # 自动打开浏览器
            if auto_open_browser and pay_url:
                print(f"\n🌐 正在打开浏览器支付页面...")
                try:
                    webbrowser.open(pay_url)
                    print("✅ 浏览器已打开，请扫码支付")
                except Exception as e:
                    print(f"⚠️  无法自动打开浏览器: {e}")
                    print(f"请手动复制链接到浏览器: {pay_url}")

    return result

def get_order_detail(order_id: str) -> Dict[str, Any]:
    """查询订单详情"""
    return call_mcp_tool("query-order", {
        "orderId": order_id
    })

# 麦麦日历
def query_calendar() -> Dict[str, Any]:
    """查询活动日历"""
    return call_mcp_tool("campaign-calendar")

# 麦麦省领券
def get_coupon_list() -> Dict[str, Any]:
    """获取可领取优惠券列表"""
    return call_mcp_tool("available-coupons")

def claim_all_coupons() -> Dict[str, Any]:
    """一键领取所有优惠券"""
    return call_mcp_tool("auto-bind-coupons")

def get_my_coupons() -> Dict[str, Any]:
    """查询我的优惠券"""
    return call_mcp_tool("query-my-coupons")

# 麦麦商城
def get_my_points() -> Dict[str, Any]:
    """查询我的积分"""
    return call_mcp_tool("query-my-account")

def get_points_products() -> Dict[str, Any]:
    """获取积分兑换商品列表"""
    return call_mcp_tool("mall-points-products")

def get_points_product_detail(product_id: str) -> Dict[str, Any]:
    """查询积分商品详情"""
    return call_mcp_tool("mall-product-detail", {
        "productId": product_id
    })

def exchange_points_product(product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """积分兑换商品"""
    return call_mcp_tool("mall-create-order", {
        "productId": product_id,
        "quantity": quantity
    })

# 通用工具
def get_current_time() -> Dict[str, Any]:
    """获取当前时间"""
    return call_mcp_tool("now-time-info")

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python mcp_client.py <command> [args...]")
        print("\n可用命令:")
        print("  nutrition_list - 获取营养信息列表")
        print("  delivery_addresses - 获取配送地址")
        print("  coupon_list - 获取优惠券列表")
        print("  claim_all_coupons - 一键领取所有优惠券")
        print("  my_coupons - 查询我的优惠券")
        print("  my_points - 查询我的积分")
        print("  points_products - 查询积分兑换商品")
        print("  calendar - 查询活动日历")
        print("  current_time - 获取当前时间")
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "nutrition_list": get_nutrition_list,
        "delivery_addresses": get_delivery_addresses,
        "coupon_list": get_coupon_list,
        "claim_all_coupons": claim_all_coupons,
        "my_coupons": get_my_coupons,
        "my_points": get_my_points,
        "points_products": get_points_products,
        "calendar": query_calendar,
        "current_time": get_current_time,
    }

    if command not in commands:
        print(f"未知命令: {command}")
        sys.exit(1)

    result = commands[command]()
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
