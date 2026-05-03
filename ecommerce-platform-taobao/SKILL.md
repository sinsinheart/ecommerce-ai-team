---
name: ecommerce-platform-taobao
description: 淘宝/天猫开放平台接口适配层。提供商品管理、订单查询、评价抓取、客服消息、售后处理、多店铺管理等核心API封装。当用户需要在淘宝/天猫平台执行电商运营操作、对接淘宝店铺数据时使用此Skill。通过此适配层实现跨平台统一数据接口。
---

# 淘宝/天猫平台适配层

淘宝开放平台（TOP）API 封装，为上层运营 Skill 提供统一的淘宝平台数据接口。

## 核心能力

- **商品管理**：读取/修改商品信息、上下架、库存同步、SKU管理
- **订单查询**：订单列表、订单详情、物流跟踪、买家信息
- **评价管理**：评价抓取、追评查询、问大家监控
- **客服消息**：旺旺消息接收、自动回复、会话管理
- **售后处理**：退款审核、退货物流、纠纷处理
- **多店铺管理**：Token管理、店铺切换、数据聚合

## 脚本清单

| 脚本 | 功能 | API端点 |
|------|------|---------|
| `scripts/auth.py` | OAuth2.0认证与Token刷新 | `oauth2/authorize`, `oauth2/token` |
| `scripts/products.py` | 商品读写、上下架、库存 | `taobao.item.get`, `taobao.item.update` |
| `scripts/orders.py` | 订单查询、物流跟踪 | `taobao.trades.sold.get` |
| `scripts/reviews.py` | 评价/追评/问大家抓取 | `taobao.traderates.get` |
| `scripts/customer_service.py` | 旺旺消息收发 | `taobao.openim.messages.get` |
| `scripts/aftersales.py` | 退款审核、退货处理 | `taobao.refunds.receive.get` |

## 使用方式

```bash
# 初始化认证（淘宝OAuth2.0授权码模式）
python scripts/auth.py init --shop-id tb001 --app-key <key> --app-secret <secret>

# 获取商品评价
python scripts/reviews.py fetch --num-iid <id> --rating 1-3 --days 7

# 修改商品信息
python scripts/products.py update --num-iid <id> --title "新标题"

# 审核售后
python scripts/aftersales.py audit --refund-id <id> --action approve
```

## 参考文档

- `references/api-reference.md` — 淘宝开放平台API详细参考
