# 店小二 — 项目总览

## 项目定位
面向中小电商商家，基于 EasyClaw 搭建店小二 AI 数字团队，自然语言配置工作流，零代码实现全链路自动化。

## 核心团队（6大Skill模块）

| # | Skill | 职责 | 触发场景 |
|---|-------|------|----------|
| 1 | ecommerce-customer-service | 智能客服代理 | 买家咨询、FAQ应答、差评风险预警 |
| 2 | ecommerce-product-optimization | 商品智能优化 | 竞品分析、标题优化、违禁词检测 |
| 3 | ecommerce-data-review | 店铺数据复盘 | 日报/周报生成、流量诊断、异常预警 |
| 4 | ecommerce-after-sales | 售后自动化处理 | 退换货审核、物流同步、恶意订单识别 |
| 5 | ecommerce-review-management | 差评智能抓取与诊断 | 差评轮询抓取、AI归因、优化建议生成 |
| 6 | ecommerce-hot-product-prediction | 全网爆款预测与上架 | 热点抓取、爆款预测、内容生成、自动上架 |

## 商业闭环
爆款选品 → 新品上架 → 售前接待 → 商品优化 → 日常复盘 → 售后处理 → 口碑治理

## 技术实现
- 平台：EasyClaw AI Agent 运行时
- 配置：零代码，自然语言驱动
- 调度：定时轮询 + 事件触发 + 异常告警
- 数据：电商后台 + 评价系统 + 全网热点 + 聊天窗口

## 目录结构
```
ecommerce-ai-team/
├── PROJECT.md              # 本文件
├── skills/                 # Skill 安装目录（注册后自动生成）
└── memory/                 # 项目记忆与运营数据
```
