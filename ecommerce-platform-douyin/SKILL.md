---
name: ecommerce-platform-douyin
description: 抖音小店开放平台接口适配层。提供商品管理、订单查询、评价抓取、客服消息、售后处理、达人带货等核心API封装。当用户需要在抖音小店执行电商运营操作、对接抖音店铺数据时使用此Skill。通过此适配层实现跨平台统一数据接口。
---

# 抖音小店平台适配层

抖音小店开放平台 API 封装，为上层运营 Skill 提供统一的抖音平台数据接口。

## 核心能力

- **商品管理**：读取/修改商品信息、上下架、库存同步、规格管理
- **订单查询**：订单列表、订单详情、物流跟踪
- **评价管理**：评价抓取、追评监控、用户反馈
- **客服消息**：飞鸽消息接收、自动回复、会话管理
- **售后处理**：退款审核、退货处理、仲裁支持
- **达人带货**：达人数据、商品分发、佣金管理
- **多店铺管理**：Token管理、店铺切换、数据聚合

## 脚本清单

| 脚本 | 功能 | API端点 |
|------|------|---------|
| `scripts/auth.py` | OAuth2.0认证与Token刷新 | `oauth2/authorize`, `oauth2/access_token` |
| `scripts/products.py` | 商品读写、上下架、库存 | `product.detail`, `product.editV2` |
| `scripts/orders.py` | 订单查询、物流跟踪 | `order.search`, `order.getOrderDetail` |
| `scripts/reviews.py` | 评价/追评抓取 | `product.getComment` |
| `scripts/customer_service.py` | 飞鸽消息收发 | 飞鸽消息Webhook |
| `scripts/aftersales.py` | 售后审核、退货处理 | `refund.search`, `refund.process` |
| `scripts/influencer.py` | 达人数据、带货分析 | `kol.product.list`, `product.distribute` |

## 使用方式

```bash
# 初始化认证（抖音OAuth2.0授权码模式）
python scripts/auth.py init --shop-id dy001 --app-key <key> --app-secret <secret>

# 获取商品评价
python scripts/reviews.py fetch --product-id <id> --rating 1-3 --days 7

# 修改商品
python scripts/products.py update --product-id <id> --title "新标题"

# 审核售后
python scripts/aftersales.py audit --refund-id <id> --action approve
```

## 参考文档

- `references/api-reference.md` — 抖音小店开放平台API详细参考
