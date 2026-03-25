#!/usr/bin/env python3
"""
麦当劳 MCP 客户端脚本
用于调用麦当劳 MCP API 的各种功能
"""

import os
import sys
import json
import time
import subprocess
import requests
import webbrowser
from typing import Dict, Any, Optional, List

MCP_BASE_URL = "https://mcp.mcd.cn"

def get_token() -> str:
    """从配置文件或环境变量获取 MCP Token"""
    # 优先从环境变量读取
    token = os.environ.get("MCD_MCP_TOKEN")
    if token:
        return token
    # 读取OpenClaw全局配置文件
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "MCD_MCP_TOKEN":
                        return value.strip()
    raise ValueError("请在~/.openclaw/.env中配置MCD_MCP_TOKEN或设置环境变量MCD_MCP_TOKEN")

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

def search_product_by_name(store_code: str, be_code: str, keyword: str) -> Optional[Dict[str, Any]]:
    """
    根据商品名称模糊搜索匹配商品
    Args:
        store_code: 门店编码
        be_code: BE编码
        keyword: 商品名称关键词
    Returns:
        匹配到的商品信息，包含productCode、name、price，没有匹配到返回None
    """
    result = get_store_products(store_code, be_code)
    if not result.get("success", True):
        return None
    
    structured_content = result.get("result", {}).get("structuredContent", {})
    if not structured_content.get("success"):
        return None
    
    data = structured_content.get("data", {})
    meals = data.get("meals", {})
    keyword = keyword.strip().lower()
    
    # 优先精确匹配
    for code, meal in meals.items():
        if meal.get("name", "").strip().lower() == keyword:
            return {
                "productCode": code,
                "name": meal.get("name"),
                "price": meal.get("currentPrice")
            }
    
    # 模糊匹配
    matches = []
    for code, meal in meals.items():
        meal_name = meal.get("name", "").strip().lower()
        if keyword in meal_name:
            matches.append({
                "productCode": code,
                "name": meal.get("name"),
                "price": meal.get("currentPrice")
            })
    
    # 返回匹配度最高的第一个结果
    if matches:
        return matches[0]
    
    return None

def parse_order_items(store_code: str, be_code: str, user_input: str) -> List[Dict[str, Any]]:
    """
    解析用户输入的商品列表，支持按商品名称/序号识别，自动转换为商品编码
    Args:
        store_code: 门店编码
        be_code: BE编码
        user_input: 用户输入的商品列表，格式支持：
                    "麦乐鸡 1, 脆汁鸡 1"
                    "1 1, 3 2"（序号+数量）
    Returns:
        订单商品列表，格式：[{"productCode": "xxx", "quantity": 1}]
    """
    items = []
    user_input = user_input.strip()
    if not user_input:
        return items
    
    # 获取商品列表用于序号匹配
    products_result = get_store_products(store_code, be_code)
    structured_content = products_result.get("result", {}).get("structuredContent", {})
    data = structured_content.get("data", {})
    meals_list = []
    for code, meal in data.get("meals", {}).items():
        meals_list.append({
            "productCode": code,
            "name": meal.get("name"),
            "price": meal.get("currentPrice")
        })
    
    # 分割用户输入的多个商品
    for item_str in user_input.split(","):
        item_str = item_str.strip()
        if not item_str:
            continue
        
        # 分割名称/序号和数量
        parts = item_str.rsplit(" ", 1)
        if len(parts) != 2:
            # 没有写数量默认1份
            name_or_index = parts[0]
            quantity = 1
        else:
            name_or_index, quantity_str = parts
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    quantity = 1
            except ValueError:
                quantity = 1
        
        # 判断是序号还是名称
        if name_or_index.isdigit():
            # 序号匹配（序号从1开始）
            index = int(name_or_index) - 1
            if 0 <= index < len(meals_list):
                items.append({
                    "productCode": meals_list[index]["productCode"],
                    "quantity": quantity
                })
        else:
            # 名称匹配
            product = search_product_by_name(store_code, be_code, name_or_index)
            if product:
                items.append({
                    "productCode": product["productCode"],
                    "quantity": quantity
                })
    
    return items

def get_product_detail(product_code: str, store_code: str, be_code: str) -> Dict[str, Any]:
    """查询餐品详情"""
    return call_mcp_tool("query-meal-detail", {
        "productCode": product_code,
        "storeCode": store_code,
        "beCode": be_code
    })

def calculate_price(store_code: str, be_code: str, items: List[Dict[str, Any]], coupon_id: Optional[str] = None) -> Dict[str, Any]:
    """计算订单价格，支持传入优惠券ID抵扣"""
    params = {
        "storeCode": store_code,
        "beCode": be_code,
        "items": items
    }
    if coupon_id:
        params["couponId"] = coupon_id
    return call_mcp_tool("calculate-price", params)

def create_delivery_order(store_code: str, be_code: str, items: List[Dict[str, Any]], coupon_id: Optional[str] = None) -> Dict[str, Any]:
    """创建外送订单，支持传入优惠券ID自动抵扣"""
    params = {
        "storeCode": store_code,
        "beCode": be_code,
        "items": items
    }
    if coupon_id:
        params["couponId"] = coupon_id
    return call_mcp_tool("create-order", params)

def create_order_and_pay(address_id: str, store_code: str, be_code: str,
                         items: List[Dict[str, Any]],
                         auto_open_browser: bool = True,
                         check_pending_orders: bool = True,
                         auto_claim_coupons: bool = True,
                         auto_use_coupon: bool = True,
                         coupon_id: Optional[str] = None) -> Dict[str, Any]:
    """
    创建外送订单并自动打开支付链接

    Args:
        address_id: 配送地址ID
        store_code: 门店编码
        be_code: BE编码
        items: 商品列表
        auto_open_browser: 是否自动打开浏览器支付页面
        check_pending_orders: 是否检查待支付订单避免重复下单
        auto_claim_coupons: 是否自动领取所有可领优惠券（默认开启）
        auto_use_coupon: 是否自动使用最优优惠券（默认开启，优先级低于指定coupon_id）
        coupon_id: 手动指定要使用的优惠券ID（优先级最高）

    Returns:
        订单信息，包含 orderId 和 payH5Url
    """
    # 检查是否有待支付订单，避免重复创建（暂时注释，官方API暂未开放订单列表查询接口）
    # if check_pending_orders:
    #     pending_result = get_pending_orders()
    #     if pending_result.get("success", True):
    #         pending_data = pending_result.get("result", {}).get("structuredContent", {}).get("data", [])
    #         if pending_data:
    #             print(f"⚠️  发现 {len(pending_data)} 个待支付订单：")
    #             for idx, order in enumerate(pending_data):
    #                 print(f"  {idx+1}. 订单号: {order.get('orderId')} | 金额: ¥{order.get('realTotalAmount', 'N/A')}")
    #                 print(f"    创建时间: {order.get('createTime')}")
    #             print("请先支付或取消待支付订单，避免重复下单！")
    #             confirm = input("是否仍要创建新订单？(y/N): ").strip().lower()
    #             if confirm != "y":
    #                 print("已取消创建新订单")
    #                 return {"success": False, "message": "用户取消创建订单"}

    # 自动领取所有优惠券
    selected_coupon_id = coupon_id
    if auto_claim_coupons and not selected_coupon_id:
        print("🔍 正在自动领取所有可领优惠券...")
        claim_result = claim_all_coupons()
        claim_success = claim_result.get("result", {}).get("structuredContent", {}).get("success", False)
        if claim_success:
            success_count = claim_result["result"]["structuredContent"]["data"].get("successCount", 0)
            print(f"✅ 成功领取 {success_count} 张优惠券")
        else:
            print("ℹ️  无可领取优惠券或领取失败")

    # 自动选择最优优惠券
    if auto_use_coupon and not selected_coupon_id:
        print("🔍 正在查询可用优惠券并选择最优...")
        coupons_result = get_store_coupons(store_code, be_code)
        if coupons_result.get("success", True):
            coupons_data = coupons_result.get("result", {}).get("structuredContent", {}).get("data", [])
            if coupons_data:
                # 按优惠金额从大到小排序，选最大的可用券
                valid_coupons = [c for c in coupons_data if c.get("status") == "AVAILABLE" and c.get("discountAmount", 0) > 0]
                if valid_coupons:
                    valid_coupons.sort(key=lambda x: x.get("discountAmount", 0), reverse=True)
                    best_coupon = valid_coupons[0]
                    selected_coupon_id = best_coupon.get("couponId")
                    print(f"✅ 自动选择最优优惠券：{best_coupon.get('couponName')}，优惠¥{best_coupon.get('discountAmount')/100:.1f}")
                else:
                    print("ℹ️  暂无可用优惠券")
            else:
                print("ℹ️  暂无可用优惠券")

    # 构造创建订单参数
    create_params = {
        "addressId": address_id,
        "storeCode": store_code,
        "beCode": be_code,
        "items": items
    }
    if selected_coupon_id:
        create_params["couponId"] = selected_coupon_id
        print(f"🎫 本次订单将使用优惠券：{selected_coupon_id}")

    result = call_mcp_tool("create-order", create_params)

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
                    # 优先使用OpenClaw内置browser工具打开支付页
                    subprocess.run([
                        "openclaw", "browser", "open", 
                        "--profile", "openclaw", 
                        "--url", pay_url
                    ], check=True, capture_output=True)
                    print("✅ 已通过OpenClaw浏览器打开支付页面，请直接扫码支付")
                except Exception as e1:
                    #  fallback到系统默认浏览器
                    try:
                        webbrowser.open(pay_url)
                        print("✅ 已打开系统默认浏览器，请扫码支付")
                    except Exception as e2:
                        print(f"⚠️  无法自动打开浏览器: {str(e1)} | {str(e2)}")
            
            # 发送支付链接消息到当前会话，方便用户选择支付方式
            if pay_url:
                print(f"\n💬 已发送支付链接到当前会话，你也可以点击链接直接支付：")
                try:
                    send_notification(f"✅ 麦当劳订单创建成功！\n📋 订单号：{order_id}\n💰 实付金额：¥{data.get('orderDetail', {}).get('realTotalAmount', 'N/A')}\n💳 支付链接：{pay_url}\n你可以直接点击链接支付，或在已打开的浏览器页面支付~")
                    print("✅ 支付链接已发送到会话")
                except Exception as e:
                    print(f"⚠️  发送支付链接失败：{e}")
                    print(f"🔗 支付链接：{pay_url}")

            # 自动启动订单状态后台监控
            if order_id:
                print(f"\n🔔 正在启动订单状态监控，支付完成后会自动通知你订单进度~")
                # 启动后台进程监控订单状态
                try:
                    subprocess.Popen([
                        sys.executable, os.path.abspath(__file__),
                        "monitor_order", order_id
                    ], cwd=os.path.dirname(os.path.abspath(__file__)),
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    start_new_session=True)
                    print("✅ 订单监控已在后台启动，状态更新会主动通知你")
                except Exception as e:
                    print(f"⚠️  启动订单监控失败: {e}，你可以手动执行监控命令")

    return result

def get_order_detail(order_id: str) -> Dict[str, Any]:
    """查询订单详情"""
    return call_mcp_tool("query-order", {
        "orderId": order_id
    })

# def get_pending_orders() -> Dict[str, Any]:
#     """查询待支付的订单列表（暂时注释，官方API暂未开放此接口）"""
#     return call_mcp_tool("query-order-list", {
#         "status": "PENDING_PAYMENT"
#     })

def send_notification(message: str) -> bool:
    """
    发送通知消息给用户，自动支持当前会话通道（webchat/feishu/微信等）
    Args:
        message: 通知内容
    Returns:
        是否发送成功
    """
    try:
        # 优先读取配置的通知通道，默认跟随当前会话
        notify_channel = os.environ.get("MCD_NOTIFY_CHANNEL", "")
        cmd = [
            "openclaw", "message", "send",
            "--message", message
        ]
        # 如果配置了飞书通道，指定发送到飞书
        if notify_channel == "feishu":
            cmd.extend(["--channel", "feishu"])
        # 调用OpenClaw消息工具发送通知
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except Exception as e:
        print(f"发送通知失败: {e}")
        #  fallback到标准输出打印
        print(f"通知内容：{message}")
        return False

def monitor_order_status(order_id: str, interval: int = 5) -> None:
    """
    监控订单状态，状态变化时主动通知用户，直到订单完成或取消
    Args:
        order_id: 要监控的订单号
        interval: 查询间隔（分钟，默认5分钟）
    """
    # 订单结束状态，监控到这些状态就停止
    FINAL_STATUSES = ["已完成", "已取消", "订单已完成", "订单已取消", "已退款"]
    last_status = ""

    print(f"🔔 开始监控订单 {order_id} 状态，每{interval}分钟查询一次...")
    send_notification(f"✅ 订单监控已启动：订单号 {order_id}\n订单状态更新时会主动通知你~")

    while True:
        try:
            # 查询订单详情
            result = get_order_detail(order_id)
            if not result.get("success", True):
                print(f"查询订单失败: {result.get('error')}，1分钟后重试...")
                time.sleep(60)
                continue

            structured_content = result.get("result", {}).get("structuredContent", {})
            if not structured_content.get("success"):
                print(f"查询订单失败: {structured_content.get('message')}，1分钟后重试...")
                time.sleep(60)
                continue

            order_data = structured_content.get("data", {})
            current_status = order_data.get("orderStatus", "未知")
            order_amount = order_data.get("realTotalAmount", "N/A")
            store_name = order_data.get("storeName", "麦当劳")

            # 状态变化时发送通知
            if current_status != last_status:
                if current_status == "待支付":
                    notification = f"⏳ 订单 {order_id} 状态更新：待支付\n金额：¥{order_amount}\n请尽快完成支付~"
                elif current_status == "制作中" or current_status == "已支付":
                    notification = f"🍔 订单 {order_id} 状态更新：制作中\n门店：{store_name}\n厨师正在为你制作美食~"
                elif current_status == "配送中":
                    delivery_info = order_data.get("deliveryInfo", {})
                    rider_name = delivery_info.get("riderNickName", "配送员")
                    rider_phone = delivery_info.get("riderMobilePhone", "")
                    expect_time = delivery_info.get("expectDeliveryTime", "预计送达时间待更新")
                    notification = f"🚚 订单 {order_id} 状态更新：配送中\n配送员：{rider_name} {rider_phone}\n预计送达：{expect_time}\n请保持电话畅通~"
                elif current_status in FINAL_STATUSES:
                    if "完成" in current_status:
                        notification = f"✅ 订单 {order_id} 状态更新：已完成\n你的美食已送达，请慢用~😋"
                    else:
                        notification = f"❌ 订单 {order_id} 状态更新：已取消\n订单监控已结束。"
                    # 发送最终状态通知后退出监控
                    send_notification(notification)
                    print(f"✅ 订单已结束监控，最终状态：{current_status}")
                    return
                else:
                    notification = f"ℹ️ 订单 {order_id} 状态更新：{current_status}"

                # 发送状态变更通知
                send_notification(notification)
                print(f"状态更新：{last_status} → {current_status}，已发送通知")
                last_status = current_status

            # 等待下一次查询
            time.sleep(interval * 60)

        except Exception as e:
            print(f"监控过程出现异常: {e}，1分钟后重试...")
            time.sleep(60)

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

    if command == "monitor_order":
        # 监控订单状态命令
        if len(sys.argv) < 3:
            print("用法: python mcp_client.py monitor_order <订单号> [查询间隔分钟]")
            sys.exit(1)
        order_id = sys.argv[2]
        interval = int(sys.argv[3]) if len(sys.argv) >=4 else 5
        monitor_order_status(order_id, interval)
        sys.exit(0)

    if command not in commands:
        print(f"未知命令: {command}")
        print("可用命令:")
        print("  nutrition_list - 获取营养信息列表")
        print("  delivery_addresses - 获取配送地址")
        print("  coupon_list - 获取优惠券列表")
        print("  claim_all_coupons - 一键领取所有优惠券")
        print("  my_coupons - 查询我的优惠券")
        print("  my_points - 查询我的积分")
        print("  points_products - 查询积分兑换商品")
        print("  calendar - 查询活动日历")
        print("  current_time - 获取当前时间")
        print("  monitor_order <订单号> [间隔] - 监控订单状态，默认间隔5分钟")
        sys.exit(1)

    result = commands[command]()
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
