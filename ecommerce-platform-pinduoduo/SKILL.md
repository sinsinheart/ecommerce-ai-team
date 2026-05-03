---
name: ecommerce-platform-pinduoduo
description: 拼多多开放平台接口适配层。提供商品管理、订单查询、评价抓取、客服消息、售后处理、多店铺管理等核心API封装。当用户需要在拼多多平台执行电商运营操作、对接拼多多店铺数据、调用拼多多开放平台接口时使用此Skill。所有6大运营Skill通过此适配层与拼多多平台交互。
---

# 拼多多平台适配层

拼多多开放平台 API 封装，为上层 7 个运营 Skill 提供统一的拼多多平台数据接口。

## 核心能力

- **商品管理**：读取/修改商品信息、上下架、库存同步
- **订单查询**：订单列表、订单详情、物流信息
- **评价管理**：评价抓取、追评查询、问答区监控
- **客服消息**：消息接收、自动回复、会话管理
- **售后处理**：退款审核、退货物流、纠纷处理
- **多店铺管理**：Token 管理、店铺切换、数据聚合

## 脚本清单

| 脚本 | 功能 | 对应 Skill |
|------|------|-----------|
| `scripts/auth.py` | 多店铺认证与Token管理 | 全部 |
| `scripts/products.py` | 商品读写、上下架、库存 | product-optimization, hot-product-prediction |
| `scripts/orders.py` | 订单查询、物流跟踪 | customer-service, data-review |
| `scripts/reviews.py` | 评价/追评/问答抓取 | review-management |
| `scripts/customer_service.py` | 客服消息收发 | customer-service |
| `scripts/aftersales.py` | 售后审核、退款、物流 | after-sales |

## 使用方式

所有脚本通过命令行调用，参数通过 JSON 或命令行参数传递。

```bash
# 初始化认证
python scripts/auth.py init --shop-id <id> --client-id <id> --client-secret <secret>

# 获取商品评价
python scripts/reviews.py fetch --goods-id <id> --rating 1-3 --days 7

# 修改商品标题
python scripts/products.py update --goods-id <id> --title "新标题"

# 审核售后申请
python scripts/aftersales.py audit --refund-id <id> --action approve
```

## 参考文档

- `references/api-reference.md` — 拼多多开放平台API详细参考
