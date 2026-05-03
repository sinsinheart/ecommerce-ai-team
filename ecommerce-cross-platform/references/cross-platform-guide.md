# 跨平台数据聚合使用指南

## 平台切换语法

用户可通过自然语言切换看板平台：

```
"切换到拼多多"          → 仅看拼多多数据
"切换到淘宝"            → 仅看淘宝/天猫数据
"切换到抖音"            → 仅看抖音小店数据
"展示全平台"            → 三平台聚合视图
"对比淘宝和拼多多"      → 两平台并排对比
```

## 跨平台选品对比

```
"对比防晒冰袖在三个平台的竞争情况"
"这个品类在哪个平台最好卖"
"抖音和拼多多哪个更适合推这款新品"
```

## 数据聚合规则

### 指标对齐
不同平台的概念统一映射：

| 统一概念 | 拼多多 | 淘宝 | 抖音 |
|----------|--------|------|------|
| 成交额 | order_amount (分) | payment (分) | order_info.pay_amount (分) |
| 访客数 | avg_visitors | 需计算 | traffic_data.uv |
| 转化率 | cpm | 成交/访客 | conversion_rate |
| 客单价 | 成交额/成交数 | 成交额/成交数 | 成交额/成交数 |
| DSR | star_rating | seller_rate_avg | quality_score |
| 差评 | 1-2星 | 1-2星+差评标签 | 1-2星 |

### 时间对齐
所有平台统一使用 Asia/Shanghai 时区，日报取昨日 00:00-23:59 数据。

### 货币对齐
统一转换为人民币元，保留两位小数。

## 看板输出格式

```json
{
  "platform": "all",
  "date": "2026-05-02",
  "shops": [
    {
      "platform": "pinduoduo",
      "shop_name": "潮流服饰旗舰店",
      "metrics": { "visitors": 1847, "orders": 86, "revenue": 4837.00, "conversion": 4.66, ... },
      "alerts": [...]
    },
    {
      "platform": "taobao",
      "shop_name": "潮流服饰旗舰店",
      "metrics": { "visitors": 2100, "orders": 95, "revenue": 6120.00, "conversion": 4.52, ... },
      "alerts": [...]
    },
    ...
  ]
}
```
