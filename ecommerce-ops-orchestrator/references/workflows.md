# 五大协作流程详解

## 流程1：差评驱动优化闭环

```
触发：ecommerce-review-management 发现差评率异常或高频差评类型
```

```
Step 1 — 差评归因（ecommerce-review-management）
  → 抓取最新差评
  → AI归因分类（八大类）
  → 统计各类占比，定位 TOP 问题类型
  → 输出：问题类型 + 严重程度 + 影响商品列表

Step 2 — 优化建议生成（ecommerce-review-management）
  → 匹配优化方案库（optimization-playbook.md）
  → 按商品/服务/供应链三维输出建议
  → 优先级排序
  → 输出：优化建议清单 + 行动优先级

Step 3 — 商品优化执行（ecommerce-product-optimization）
  → 接收高优先级商品列表
  → 批量优化标题/详情页/主图
  → 违禁词检测
  → 输出：优化后的商品内容

Step 4 — 效果追踪（ecommerce-data-review）
  → 监控优化后商品的差评率变化
  → 7天后复查同类差评是否下降
  → 输出：优化效果报告
```

**数据流：**
```
差评数据 → 归因分析 → 优化建议 → 商品修改 → 效果验证
```

---

## 流程2：爆款选品上架全流程

```
触发：定时扫描 or 商家主动发起选品
```

```
Step 1 — 全网热点抓取（ecommerce-hot-product-prediction）
  → 多平台数据采集
  → 数据清洗去重
  → 输出：热点商品候选池

Step 2 — AI爆款预测（ecommerce-hot-product-prediction）
  → 六大维度评分
  → 爆款分类（短期/长效/季节/蓝海）
  → 输出：爆款推荐清单 + 预测理由

Step 3 — 商品内容生成（ecommerce-hot-product-prediction）
  → 抓取优质竞品内容
  → AI生成标题/详情页/主图文案
  → 差异化优化
  → 输出：待上架商品内容

Step 4 — 合规审核（ecommerce-product-optimization）
  → 违禁词检测
  → 类目匹配校验
  → 价格/库存/规格完整性校验
  → 输出：审核结果（通过/需修改/不合规）

Step 5 — 自动上架（ecommerce-hot-product-prediction）
  → 填写商品信息
  → 多平台同步上架
  → 输出：上架结果 + 商品链接

Step 6 — 数据追踪（ecommerce-data-review）
  → 监控新品访客/转化/销量
  → 7日/14日/30日数据复盘
  → 对比预测数据
  → 输出：新品表现报告 + 迭代建议
```

---

## 流程3：日常运营驾驶舱

```
触发：每日定时 or 商家主动查看
```

```
Step 1 — 数据采集（ecommerce-data-review）
  → 抓取流量/转化/成交/客单价等核心指标
  → 对比昨日/上周同期

Step 2 — 异常诊断（ecommerce-data-review）
  → 触发预警的指标 → 深度诊断
  → 流量问题 → 联动商品优化
  → 转化问题 → 联动差评分析 + 竞品对比

Step 3 — 跨模块协同响应
  → 流量下降 + 差评上升 → 口碑治理优先
  → 转化下降 + 竞品降价 → 商品优化 + 定价调整
  → 退货率上升 + 质量问题差评 → 售后 + 供应链优化

Step 4 — 日报生成与推送
  → 汇总所有模块数据
  → 生成可视化日报
  → 推送至商家
```

---

## 流程4：售后纠纷全链路处理

```
触发：买家发起售后申请
```

```
Step 1 — 智能审核（ecommerce-after-sales）
  → 自动审核规则匹配
  → 自动通过 / 升级人工 / 自动拒绝

Step 2 — 恶意识别（ecommerce-after-sales）
  → 买家信誉评分
  → 异常行为检测
  → 标记风险订单

Step 3 — 关联差评预警（ecommerce-customer-service + ecommerce-review-management）
  → 售后原因含负面情绪 → 差评风险标记
  → 主动触达安抚（客服模块）
  → 跟进处理结果，防止差评

Step 4 — 物流追踪（ecommerce-after-sales）
  → 退货物流自动追踪
  → 签收自动确认退款
  → 异常物流告警

Step 5 — 闭环归档
  → 售后数据汇总至复盘模块
  → 退货原因归因至口碑模块
  → 高频退货商品标记
```

---

## 流程5：店铺健康度巡检

```
触发：每日/每周自动化
```

```
Step 1 — 综合体检（ecommerce-data-review）
  → DSR评分：商品+服务+物流三维检查
  → 转化率：是否低于行业均值
  → 流量趋势：是否持续下降
  → 退货率/纠纷率：是否超标

Step 2 — 短板定位
  → DSR商品分低 → 差评归因 + 商品优化
  → DSR服务分低 → 客服质检 + 售后服务优化
  → DSR物流分低 → 物流渠道评估 + 包装升级建议

Step 3 — 精准调度
  → 按短板类型自动调度对应 Skill
  → 输出综合整改方案
  → 追踪整改效果
```
