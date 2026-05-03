# 淘宝/天猫开放平台 API 参考

## 基本信息

- **API网关**: `https://eco.taobao.com/router/rest`
- **授权端点**: `https://oauth.taobao.com/authorize`
- **Token端点**: `https://oauth.taobao.com/token`
- **认证方式**: OAuth 2.0 授权码模式
- **签名方式**: MD5 (app_secret)
- **数据格式**: JSON/XML

## 认证流程

1. 在淘宝开放平台创建应用，获取 `app_key` 和 `app_secret`
2. 引导商家访问授权URL获取 `authorization_code`
3. 用 `code` 换取 `access_token`（有效期30天，需定时刷新）
4. 每次API调用携带 `access_token` 和服务端签名

```
授权URL模板:
https://oauth.taobao.com/authorize?response_type=code&client_id={app_key}
  &redirect_uri={redirect_uri}&state={state}
```

## 核心API

### 商品管理
| API | 方法 | 说明 |
|-----|------|------|
| taobao.item.get | GET | 获取商品详情 |
| taobao.item.update | POST | 修改商品信息 |
| taobao.item.update.delisting | POST | 商品下架 |
| taobao.item.update.listing | POST | 商品上架 |
| taobao.items.onsale.get | GET | 在售商品列表 |
| taobao.item.sku.get | GET | 获取SKU列表 |
| taobao.item.sku.update | POST | 修改SKU信息 |

### 订单管理
| API | 方法 | 说明 |
|-----|------|------|
| taobao.trades.sold.get | GET | 卖家已卖出的交易列表 |
| taobao.trade.get | GET | 单笔交易详情 |
| taobao.logistics.trace.search | GET | 物流流转信息查询 |

### 评价管理
| API | 方法 | 说明 |
|-----|------|------|
| taobao.traderates.get | GET | 评价列表（含追评） |
| taobao.traderate.search | GET | 搜索评价 |
| taobao.traderate.list.add | POST | 卖家解释评价 |

### 客服消息
| API | 方法 | 说明 |
|-----|------|------|
| taobao.openim.messages.get | GET | 获取IM消息列表 |
| taobao.openim.messages.send | POST | 发送IM消息 |
| taobao.openim.custmsg.push | POST | 推送客服消息 |

### 售后管理
| API | 方法 | 说明 |
|-----|------|------|
| taobao.refunds.receive.get | GET | 查询退款列表 |
| taobao.refund.get | GET | 单笔退款详情 |
| taobao.refund.refuse | POST | 拒绝退款 |
| taobao.refund.agree | POST | 同意退款 |
| taobao.rp.returngoods.refuse | POST | 拒绝退货 |
| taobao.rp.returngoods.agree | POST | 同意退货 |

### 数据统计
| API | 方法 | 说明 |
|-----|------|------|
| taobao.tbk.dg.material.optional | GET | 淘客物料搜索（竞品数据） |
| taobao.ju.items.search | GET | 聚划算商品搜索 |

## 字段映射（与拼多多对比）

| 概念 | 拼多多 | 淘宝/天猫 |
|------|--------|----------|
| 商品ID | goods_id | num_iid |
| SKU ID | sku_id | sku_id |
| 订单ID | order_sn | tid |
| 退款ID | refund_id | refund_id |
| 店铺ID | mall_id | 默认无多店（user_nick区分） |
| 类目ID | cat_id | cid |
| 商品标题 | goods_name | title |
| 商品价格 | min_group_price (拼单价) | price |
