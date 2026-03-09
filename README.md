# 麦当劳 外送点餐 Skill（基于MCP实现）

> 通过 AI Agent 自动化麦当劳点餐、优惠券管理、积分查询等操作。适合OpenClaw。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 简介

这是一个基于麦当劳中国 MCP（Model Context Protocol）开放平台的 AI Agent Skill，让你可以通过自然语言与 AI 对话来完成麦当劳相关操作，无需手动打开 App。

**核心功能：**
- 🎫 优惠券管理（查询、领取、使用）
- 🍔 外送点餐（查询餐品、创建订单、自动支付）
- ⭐ 积分系统（查询积分、浏览兑换商品、积分兑换）
- 📅 活动日历（查看最新营销活动）
- 🥗 营养信息（160+ 餐品营养数据查询）
- 📍 地址管理（添加、查询配送地址）

## 快速开始

### 1. 获取麦当劳 MCP Token

1. 访问 [麦当劳开放平台](https://open.mcd.cn/mcp/doc)
2. 点击右上角"登录"，使用手机号验证登录
3. 进入"控制台" → 点击"激活"
4. 同意服务协议
5. 复制生成的 Token

### 2. 安装 Skill
#### 从源码安装

```bash
# 克隆仓库
git clone git@github.com:jinchao-ai/mcdonald-skill.git

# 复制到 Openclaw skills 目录
cp -r mcdonald-skill ~/.openclaw/workspace/skills

```

### 3. 配置环境变量

```bash
# 添加 Token 到环境变量
echo 'export MCD_MCP_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### 4. 开始使用

与 AI 对话即可：

```
"帮我查询麦当劳的优惠券"
"我要点一个xxxx和xxxx"
"查看我的积分"
"帮我领取所有优惠券"
```

## 使用示例

### 场景 1：查询并领取优惠券

**你说：** "帮我查询麦当劳有什么优惠券"

**AI 自动执行：**
- 查询可领取优惠券列表
- 显示优惠券详情（名称、价格、有效期）

**你说：** "帮我领取所有优惠券"

**AI 自动执行：**
- 一键领取所有可用优惠券
- 显示领取结果

### 场景 2：快速点外卖

**你说：** "帮我点一份xxxx中套餐"

**AI 自动执行：**
1. 查询你的配送地址
2. 获取门店信息和餐品列表
3. 计算订单价格
4. 创建订单
5. 自动打开浏览器支付页面

**结果：** 扫码支付，等外卖送达

### 场景 3：使用优惠券点餐

**你说：** "用 14元xxxx买一送一的券下单"

**AI 自动执行：**
1. 查询你的优惠券
2. 找到对应的优惠券
3. 查询适用商品
4. 创建订单（自动应用优惠券）
5. 打开浏览器支付

### 场景 4：查询积分和兑换

**你说：** "查看我的积分"

**AI 显示：**
- 可用积分
- 累计积分
- 已过期积分

**你说：** "有什么可以兑换的商品"

**AI 显示：**
- 积分兑换商品列表
- 所需积分和商品详情

## 功能详解

### 优惠券管理

```python
# 查询可领取优惠券
python scripts/mcp_client.py coupon_list

# 一键领取所有优惠券
python scripts/mcp_client.py claim_all_coupons

# 查询我的优惠券
python scripts/mcp_client.py my_coupons
```

### 外送点餐

```python
# 查询配送地址
python scripts/mcp_client.py delivery_addresses

# 使用 Python 客户端创建订单
from scripts.mcp_client import create_order_and_pay

result = create_order_and_pay(
    address_id='xxxx',
    store_code='xxxx',
    be_code='xxxx',
    items=[
        {'productCode': 'xxxx', 'quantity': 1},  # xxxx
        {'productCode': 'xxxx', 'quantity': 1}   # xxxx
    ],
    auto_open_browser=True  # 自动打开浏览器支付
)
```

### 积分查询

```python
# 查询我的积分
python scripts/mcp_client.py my_points

# 查询积分兑换商品
python scripts/mcp_client.py points_products
```

### 营养信息

```python
# 查询餐品营养信息
python scripts/mcp_client.py nutrition_list
```

### 活动日历

```python
# 查询活动日历
python scripts/mcp_client.py calendar
```

## 项目结构

```
mcdonald-skill/
├── SKILL.md                    # Skill 主文档
├── scripts/
│   └── mcp_client.py          # Python 客户端脚本
└── references/
    └── api-reference.md       # API 参考文档
```

## 技术架构

### 工作原理

1. **Skill 触发**：AI 根据用户输入匹配到 mcdonald-skill Skill
2. **读取文档**：加载 SKILL.md 了解如何使用
3. **调用 API**：通过 Python 脚本调用麦当劳 MCP API
4. **返回结果**：将结果展示给用户

### 核心技术

- **MCP 协议**：麦当劳开放平台的 Model Context Protocol
- **Python 客户端**：封装 API 调用逻辑
- **自动化流程**：自动打开浏览器支付、自动查询地址等

## 测试结果

| 功能 | 状态 | 说明 |
|------|------|------|
| 优惠券查询 | ✅ | 7/7 成功 |
| 一键领券 | ✅ | 7/7 成功 |
| 积分查询 | ✅ | 正常 |
| 营养信息 | ✅ | 160+ 餐品 |
| 地址管理 | ✅ | 添加、查询正常 |
| 创建订单 | ✅ | 成功 |
| 浏览器打开 | ✅ | 自动打开 |
| 订单查询 | ✅ | 状态正常 |

**测试环境：**
- OS: Ubuntu 22.04
- Python: 3.10
- 测试时间: 2026-03-09

## 常见问题

### Q: 如何获取配送地址的 addressId？

A: 首次添加地址后，API 会返回 `addressId`、`storeCode`、`beCode`，这些信息会自动保存。后续查询地址时可以获取。

### Q: 为什么创建订单失败？

A: 请确保：
1. 已添加配送地址
2. Token 有效且未过期
3. 门店在营业时间内
4. 商品编码正确

### Q: 支付链接打不开怎么办？

A: 支付链接需要在麦当劳 App 或浏览器中打开。如果自动打开失败，可以手动复制链接到浏览器。

### Q: Token 会过期吗？

A: Token 有有效期，过期后需要重新登录麦当劳开放平台获取新 Token。

## 成本分析

- **开发时间**：约 4 小时
- **Token 成本**：免费（麦当劳提供）
- **维护成本**：几乎为零

**值得吗？**

如果你一周点 2 次麦当劳，每次节省 2 分钟，一年就是 3.5 小时。

更重要的是，这个思路可以复用到其他场景：美团外卖、滴滴打车、京东购物等。

## 后续计划

### 已实现功能
- ✅ 查询优惠券
- ✅ 领取优惠券
- ✅ 查询积分
- ✅ 创建订单
- ✅ 查询订单状态
- ✅ 自动打开浏览器支付

### 计划功能
- 🔲 常用订单快捷下单
- 🔲 优惠券智能推荐
- 🔲 营养搭配建议
- 🔲 价格监控

欢迎提 Issue 或 PR！

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢
- 感谢麦当劳中国开放平台提供 MCP API

如果这个项目对你有帮助，欢迎 ⭐ Star 支持！

有问题可以在 [Issues](https://github.com/jinchao-ai/mcdonald-skill/issues) 中提出。
