# 自动化调度配置指南

## 定时任务配置（EasyClaw Cron）

使用 EasyClaw cron 创建以下定时任务，实现全自动化运营。

### 每日任务

#### 07:00 — 全网热点扫描 + 爆款预测
```json
{
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "执行全网热点扫描和爆款预测：扫描电商平台、短视频、种草平台最新热点商品，运用六大维度模型预测潜力爆款，输出爆款推荐清单。使用 ecommerce-hot-product-prediction skill。"
  }
}
```

#### 08:00 — 店铺数据日报
```json
{
  "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "生成今日店铺数据日报：抓取昨日流量、转化率、成交额、客单价等核心数据，对比前日变化，诊断异常指标，输出优化建议。使用 ecommerce-data-review skill。推送日报至商家。"
  }
}
```

#### 09:00 — 差评全量抓取
```json
{
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "执行差评全量抓取和归因分析：轮询所有商品最新差评/中评/追评，AI归因分类八大类，统计分布，定位核心短板。若差评率超标则触发预警。使用 ecommerce-review-management skill。"
  }
}
```

#### 12:00 — 售后批量处理
```json
{
  "schedule": { "kind": "cron", "expr": "0 12 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "批量处理售后申请：审核待处理退货退款申请，按规则自动通过/拒绝/升级人工，识别恶意订单，追踪物流状态。使用 ecommerce-after-sales skill。"
  }
}
```

#### 18:00 — 差评日报推送
```json
{
  "schedule": { "kind": "cron", "expr": "0 18 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "生成今日差评日报：汇总今日差评数、差评率、归因分布、问题TOP商品、预警状态。若触发预警，附带优化建议优先级。使用 ecommerce-review-management skill。"
  }
}
```

### 每周任务

#### 周一 09:30 — 周报 + 选品周报
```json
{
  "schedule": { "kind": "cron", "expr": "30 9 * * 1", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "生成上周店铺运营周报和选品周报：汇总7天数据趋势，竞品动态追踪，下周优化重点。同时复盘上周爆款预测准确率，输出新一周选品建议。使用 ecommerce-data-review + ecommerce-hot-product-prediction skill。"
  }
}
```

#### 周三 10:00 — 竞品深度分析
```json
{
  "schedule": { "kind": "cron", "expr": "0 10 * * 3", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "执行竞品深度分析：抓取直接竞品和标杆竞品最新数据，分析标题/价格/主图/评价变化，识别机会和威胁。使用 ecommerce-product-optimization skill。"
  }
}
```

### 实时监控（事件驱动）

以下任务不通过 cron，而是由业务流程自动触发：

| 触发事件 | 响应动作 | 涉及 Skill |
|---------|---------|-----------|
| 买家发送咨询消息 | 自动应答 | `ecommerce-customer-service` |
| 售后申请提交 | 自动审核 | `ecommerce-after-sales` |
| 差评率超过阈值 | 即时预警 + 归因 | `ecommerce-review-management` |
| DSR连续下降 | 短板诊断 + 调度优化 | orchestrator 串联多Skill |
| 发现高概率爆款 | 推送预览待确认 | `ecommerce-hot-product-prediction` |
| 物流异常 | 告警 + 跟进 | `ecommerce-after-sales` |

## 首次部署步骤

1. 确认所有 6 个 Skill 已注册
2. 配置店铺数据源（电商平台API密钥）
3. 配置推送渠道（飞书/企业微信 webhook）
4. 使用 EasyClaw cron 创建上述定时任务
5. 设置监控阈值（差评率、流量下降比例等）
6. 启动自动化运营
