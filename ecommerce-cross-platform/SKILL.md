---
name: ecommerce-cross-platform
description: 跨平台电商数据聚合看板。统一展示拼多多/淘宝/抖音多店铺核心指标（流量/转化/差评率），支持平台切换、跨平台选品对比、多店数据聚合。当用户需要查看多平台数据、对比各平台表现、切换平台看板、跨平台选品比较时使用此Skill。
---

# 跨平台数据聚合看板

统一管理拼多多、淘宝、抖音小店三平台店铺数据，提供一站式跨平台运营视图。

## 核心能力

- **统一数据看板**：跨平台核心指标汇总（流量/转化/成交/客单价/差评率）
- **平台切换**：一键切换单平台详情 vs 多平台聚合视图
- **跨平台选品对比**：同品类在三平台的热度/价格/竞争对比
- **多店趋势图**：多店铺核心指标趋势对比
- **异常聚合预警**：跨平台异常统一告警

## 脚本清单

| 脚本 | 功能 |
|------|------|
| `scripts/cross_dashboard.py` | 跨平台数据聚合与看板生成 |
| `scripts/cross_selection.py` | 跨平台选品对比分析 |

## 数据源

| 平台 | Skill |
|------|-------|
| 拼多多 | ecommerce-platform-pinduoduo |
| 淘宝/天猫 | ecommerce-platform-taobao |
| 抖音小店 | ecommerce-platform-douyin |

## 看板指标

### 核心指标（所有平台统一）
- 访客数 / 浏览量 / 成交单数 / 成交额 / 转化率 / 客单价 / DSR评分

### 差评指标
- 差评数 / 差评率 / 主要归因 / 预警状态

### 商品指标
- TOP5商品 / 新品表现 / 库存告警

## 使用方式

```bash
# 跨平台数据看板
python scripts/cross_dashboard.py dashboard --date today

# 跨平台选品对比
python scripts/cross_selection.py compare --keyword "防晒冰袖"

# 平台切换
python scripts/cross_dashboard.py switch --platform pinduoduo
python scripts/cross_dashboard.py switch --platform taobao
python scripts/cross_dashboard.py switch --platform douyin
python scripts/cross_dashboard.py switch --platform all

# 异常聚合预警
python scripts/cross_dashboard.py alerts
```

## 参考文档

- `references/cross-platform-guide.md` — 跨平台使用指南
