---
name: ecommerce-ops-orchestrator
description: 电商运营总调度，串联智能客服、商品优化、数据复盘、售后处理、差评运维、爆款预测六大Skill协同工作，支持拼多多/淘宝/抖音三平台统一调度与数据聚合。自动识别用户意图并路由到对应Skill和平台，管理跨模块协作流程，调度每日/每周自动化任务。当用户需要管理电商店铺整体运营、启动自动化工作流、协调多个运营任务、切换或对比多平台数据时使用此Skill。
---

# 电商运营总调度

总调度 Agent，统一管理 6 大运营 Skill 的协同工作，实现全链路电商自动化闭环。

## 团队能力地图

| Skill | 触发关键词 | 核心能力 |
|-------|-----------|----------|
| `ecommerce-customer-service` | 客服、接待、回复、买家咨询、FAQ | 自动应答、差评风险预警 |
| `ecommerce-product-optimization` | 优化商品、标题、详情页、违禁词、竞品 | 竞品分析、AI改写、违禁词检测 |
| `ecommerce-data-review` | 数据、复盘、日报、周报、流量诊断 | 数据采集、异常诊断、报告生成 |
| `ecommerce-after-sales` | 售后、退换货、退款、恶意订单 | 自动审核、物流追踪、欺诈识别 |
| `ecommerce-review-management` | 差评、口碑、评价、归因、优化建议 | 差评抓取、AI归因、优化建议 |
| `ecommerce-hot-product-prediction` | 爆款、选品、热点、趋势、上架 | 趋势抓取、爆款预测、自动上架 |
| `ecommerce-cross-platform` | 跨平台、全平台、切换、对比、聚合 | 多平台看板、平台切换、跨平台选品对比 |

## 平台适配层

| Skill | 平台 | 说明 |
|-------|------|------|
| `ecommerce-platform-pinduoduo` | 🔵 拼多多 | 商品/订单/评价/售后/客服 API |
| `ecommerce-platform-taobao` | 🟠 淘宝/天猫 | 商品/订单/评价/售后/旺旺 API |
| `ecommerce-platform-douyin` | ⚫ 抖音小店 | 商品/订单/评价/售后/飞鸽/达人 API |

## 意图路由规则

收到用户请求后，按以下优先级匹配：

```
Task Progress:
- [ ] 识别用户意图关键词
- [ ] 匹配目标 Skill（可多选）
- [ ] 判断是否为跨模块协作流程
- [ ] 调度对应 Skill 执行
```

**单Skill 路由：**
- 仅涉及一个模块 → 直接调度对应 Skill + 默认平台（拼多多）
- 例：「帮我看看今天差评情况」→ `ecommerce-review-management` + `platform-pinduoduo`

**多平台路由（根据关键词识别）：**
- 提到"淘宝/天猫" → 调度 `ecommerce-platform-taobao`
- 提到"抖音/抖店" → 调度 `ecommerce-platform-douyin`
- 提到"跨平台/全平台/对比/切换/聚合" → 调度 `ecommerce-cross-platform`
- 未指定平台 → 默认拼多多，同时提示可切换平台

**多Skill 串联路由（跨模块协作）：**
- 涉及多个模块有因果/依赖关系 → 按协作流程执行
- 例：「发现差评集中在尺码问题，帮我优化相关商品」→ `ecommerce-review-management` → `ecommerce-product-optimization`

## 五大协作流程

详见 `references/workflows.md`：

1. **差评驱动优化闭环**：差评发现 → 归因分析 → 优化建议 → 商品优化执行 → 效果追踪
2. **爆款选品上架全流程**：热点发现 → 爆款预测 → 内容生成 → 合规审核 → 自动上架 → 数据追踪
3. **日常运营驾驶舱**：数据采集 → 异常诊断 → 多模块协同响应 → 日报推送
4. **售后纠纷全链路处理**：售后申请 → 智能审核 → 恶意识别 → 物流追踪 → 闭环归档
5. **店铺健康度巡检**：DSR/转化率/流量综合体检 → 短板定位 → 精准调度优化模块

## 自动化调度配置

使用 EasyClaw cron 配置定时任务，详见 `references/scheduling.md`。

**推荐调度计划：**

| 时间 | 任务 | 调度 Skill |
|------|------|-----------|
| 07:00 | 全网热点扫描 + 爆款预测 | `ecommerce-hot-product-prediction` |
| 08:00 | 店铺数据日报生成 | `ecommerce-data-review` |
| 09:00 | 差评全量抓取 + 归因 | `ecommerce-review-management` |
| 10:00 | 竞品动态追踪 | `ecommerce-product-optimization` |
| 12:00 | 售后审批批量处理 | `ecommerce-after-sales` |
| 15:00 | 低流量商品诊断 | `ecommerce-product-optimization` |
| 18:00 | 差评日报 + 预警推送 | `ecommerce-review-management` |
| 20:00 | 爆款新品数据复盘 | `ecommerce-hot-product-prediction` |
| 周一09:00 | 周报 + 选品周报 | `ecommerce-data-review` + `ecommerce-hot-product-prediction` |

6. **跨平台数据聚合**：用户请求 → 平台识别 → 数据采集 → 统一看板 → 对比分析

## 推送与通知

- 日报/周报 → 推送至商家飞书/企业微信
- 差评预警 → 即时推送 + 标记优先级
- 爆款发现 → 推送预览，待商家确认后上架
- 异常告警 → 即时推送，包含诊断和建议
