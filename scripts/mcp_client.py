        items = parse_order_items(store_code, be_code, user_input)
        result = create_order_and_pay(address_id, store_code, be_code, items)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    elif command == "query_order":
        # 查询订单详情命令
        if len(sys.argv) < 3:
            print("用法: python mcp_client.py query_order <订单号>")
            sys.exit(1)
        order_id = sys.argv[2]
        result = get_order_detail(order_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    elif command == "exchange_points":
        # 积分兑换商品命令
        if len(sys.argv) < 3:
            print("用法: python mcp_client.py exchange_points <product_id> [数量]")
            sys.exit(1)
        product_id = sys.argv[2]
        quantity = int(sys.argv[3]) if len(sys.argv) >=4 else 1
        result = exchange_points_product(product_id, quantity)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    if command not in commands:
        print(f"未知命令: {command}")
        print("可用命令:")
        print("  nutrition_list - 获取营养信息列表")
        print("  delivery_addresses - 获取配送地址")
        print("  add_address <省份> <城市> <区县> <详细地址> <联系人> <电话> [是否默认(0/1)] - 添加配送地址")
        print("  coupon_list - 获取可领取优惠券列表")
        print("  claim_all_coupons - 一键领取所有优惠券")
        print("  claim_coupon <coupon_id> - 领取指定优惠券")
        print("  my_coupons - 查询我的优惠券")
        print("  my_points - 查询我的积分")
        print("  points_products - 查询积分兑换商品")
        print("  exchange_points <product_id> [数量] - 积分兑换商品")
        print("  calendar - 查询活动日历")
        print("  current_time - 获取当前时间")
        print("  query_meals <store_code> <be_code> - 查询门店可售餐品列表")
        print("  search_meal <store_code> <be_code> <关键词> - 按名称搜索商品")
        print("  meal_detail <product_code> <store_code> <be_code> - 查询餐品详情/营养信息")
        print("  store_coupons <store_code> <be_code> - 查询门店可用优惠券")
        print("  calculate_price <store_code> <be_code> <\"商品列表\"> - 计算订单价格，商品格式：\"麦辣鸡腿堡 1, 中薯条 2\"")
        print("  create_order <address_id> <store_code> <be_code> <\"商品列表\"> - 创建订单并打开支付页")
        print("  query_order <订单号> - 查询订单详情/状态")
        print("  monitor_order <订单号> [间隔分钟] - 监控订单状态，默认间隔5分钟")
        sys.exit(1)

    result = commands[command]()
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
