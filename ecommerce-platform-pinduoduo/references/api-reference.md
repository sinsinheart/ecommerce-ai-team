# 拼多多开放平台 API 参考

## 认证方式

### OAuth 2.0 授权流程
```
1. 在拼多多开放平台创建应用，获取 client_id + client_secret
2. 引导商家授权，获取 authorization_code
3. 用 authorization_code 换取 access_token
4. access_token 过期后使用 refresh_token 刷新
```

### 签名算法
```
sign = MD5(client_secret + key1value1 + key2value2 + ... + client_secret)
- 按参数名ASCII码升序排列
- 参数值直接拼接，不加分隔符
- 最终字符串两端拼接 client_secret
```

### 公共参数
| 参数 | 说明 |
|------|------|
| type | API方法名，如 pdd.goods.list.get |
| client_id | 应用ID |
| access_token | 商家授权Token |
| timestamp | 时间戳（秒） |
| data_type | 响应格式，固定 JSON |
| sign | MD5签名 |

---

## 商品API

### pdd.goods.list.get — 商品列表
```
入参: page, page_size, goods_status(可选)
返回: goods_list[{goods_id, goods_name, price, quantity, ...}]
```

### pdd.goods.detail.get — 商品详情
```
入参: goods_id
返回: goods_detail{goods_name, goods_desc, price, sku_list, pv_7d, ...}
```

### pdd.goods.commit — 修改商品
```
入参: goods_id, goods_name(可选), goods_desc(可选), ...
返回: success标志
注意：修改后需要平台审核
```

### pdd.goods.quantity.update — 更新库存
```
入参: goods_id, sku_id, quantity
返回: success标志
```

### pdd.goods.sale.status.set — 上下架
```
入参: goods_id, is_onsale(1=上架, 0=下架)
返回: success标志
```

### pdd.goods.add — 新增商品
```
入参: goods_name, goods_desc, cat_id, market_price, ...
返回: goods_id
```

---

## 评价API

### pdd.goods.comments.get — 商品评价
```
入参: goods_id, page, page_size, rating(可选)
返回: comments_list[{comment, rating, user_name, comment_time, append_comment, ...}]
注意：单次最多返回50条
```

---

## 订单API

### pdd.order.list.get — 订单列表
```
入参: page, page_size, order_status(可选)
返回: order_list[{order_sn, goods_name, order_amount, order_time, ...}]
```

### pdd.order.detail.get — 订单详情
```
入参: order_sn
返回: order_detail{...receiver_address, receiver_phone, ship_time, ...}
```

---

## 售后API

### pdd.refund.list.get — 售后列表
```
入参: page, page_size, refund_status(可选)
返回: refund_list[{refund_id, goods_name, refund_amount, ...}]
```

### pdd.refund.detail.get — 售后详情
```
入参: refund_id
返回: refund_detail{buyer_name, refund_reason, apply_time, ...}
```

### pdd.refund.approve — 同意退款
```
入参: refund_id
返回: success标志
```

### pdd.refund.refuse — 拒绝退款
```
入参: refund_id, refuse_reason
返回: success标志
```

---

## 客服API

### pdd.message.list.get — 消息列表
```
入参: page_size
返回: message_list[{user_id, user_name, content, time, ...}]
```

### pdd.message.send — 发送消息
```
入参: to_user_id, content
返回: success标志
注意：平台限制5分钟内未回复会扣分
```

---

## 调用限制

| 限制项 | 限制值 |
|-------|-------|
| QPS上限 | 10次/秒（普通应用） |
| 评价抓取频率 | 建议每30分钟一次 |
| 商品修改频率 | 建议间隔10分钟 |
| 客服消息 | 5分钟内回复率影响DSR |

## 错误码

| 错误码 | 说明 | 处理 |
|-------|------|------|
| 10001 | Token过期 | 自动调用refresh |
| 10002 | 签名错误 | 检查签名算法 |
| 10003 | 参数错误 | 检查必填参数 |
| 20001 | 频率限制 | 降低请求频率 |
| 30001 | 商品不存在 | 检查goods_id |
| 40001 | 售后单不存在 | 检查refund_id |
