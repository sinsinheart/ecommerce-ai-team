# 抖音小店开放平台 API 参考

## 基本信息

- **API网关**: `https://open-api.fuxi.douyin.com`
- **授权端点**: `https://open.douyin.com/platform/oauth/connect`
- **Token端点**: `https://open-api.fuxi.douyin.com/oauth2/access_token`
- **认证方式**: OAuth 2.0 授权码模式
- **签名方式**: SHA256 + app_secret
- **数据格式**: JSON

## 认证流程

1. 在抖音开放平台创建应用，获取 `app_key` 和 `app_secret`
2. 引导商家访问授权URL，选择要授权的店铺
3. 用 `auth_code` 换取 `access_token`（有效期默认30天）
4. 每次API调用携带 `access-token` Header

```
授权URL模板:
https://open.douyin.com/platform/oauth/connect?client_key={app_key}
  &response_type=code&scope=product_base,order_base
  &redirect_uri={redirect_uri}&state={state}
```

## 核心API

### 商品管理
| API | 方法 | 说明 |
|-----|------|------|
| /product/detail | POST | 获取商品详情 |
| /product/listV2 | POST | 获取商品列表 |
| /product/editV2 | POST | 修改商品信息 |
| /product/addV2 | POST | 新增商品 |
| /product/setOffline | POST | 下架商品 |
| /product/setOnline | POST | 上架商品 |
| /sku/detail | POST | 获取SKU详情 |
| /sku/editCode | POST | 修改SKU编码 |

### 订单管理
| API | 方法 | 说明 |
|-----|------|------|
| /order/search | POST | 订单搜索/列表 |
| /order/getOrderDetail | POST | 订单详情 |
| /order/BatchSearchIndex | POST | 批量查询订单状态 |
| /order/logisticsAdd | POST | 发货 |

### 评价管理
| API | 方法 | 说明 |
|-----|------|------|
| /product/getComment | POST | 获取商品评价 |
| /product/replyComment | POST | 回复评价 |
| /product/getAppealList | POST | 申诉列表 |

### 售后管理
| API | 方法 | 说明 |
|-----|------|------|
| /refund/search | POST | 售后/退款列表 |
| /refund/getDetail | POST | 售后详情 |
| /refund/process | POST | 处理售后申请 |
| /refund/shopRefund | POST | 商家主动退款 |

### 客服消息（飞鸽）
| API | 方法 | 说明 |
|-----|------|------|
| /im/sendMsg | POST | 发送消息 |
| /im/getMsgList | POST | 获取消息列表 |
| /im/recallMsg | POST | 撤回消息 |

### 达人带货
| API | 方法 | 说明 |
|-----|------|------|
| /kol/product/list | POST | 达人带货商品列表 |
| /product/distribute | POST | 设置商品分销 |
| /alliance/getAuthorizeInfo | POST | 获取达人授权信息 |

### 数据罗盘
| API | 方法 | 说明 |
|-----|------|------|
| /data/liveRoomData | POST | 直播间数据 |
| /data/shopData | POST | 店铺整体数据 |
| /data/productData | POST | 商品数据 |
| /data/trafficData | POST | 流量数据 |

## 字段映射（与拼多多对比）

| 概念 | 拼多多 | 抖音小店 |
|------|--------|----------|
| 商品ID | goods_id | product_id |
| SKU ID | sku_id | sku_id |
| 订单ID | order_sn | order_id |
| 退款ID | refund_id | refund_id |
| 店铺ID | mall_id | shop_id |
| 商品标题 | goods_name | title |
| 商品价格 | min_group_price | price (分) |

## 特色能力

- **直播电商**: 专属直播数据分析、商品讲解分析
- **内容电商**: 短视频挂车数据、达人分销追踪
- **兴趣推荐**: 基于内容标签的流量分析
