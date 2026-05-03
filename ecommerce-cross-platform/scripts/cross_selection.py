#!/usr/bin/env python3
"""
跨平台选品对比分析
对比同一品类在拼多多/淘宝/抖音的热度、竞争、定价策略
"""

import json
import argparse

# 跨平台选品对比数据（模拟，实际接入后从各平台获取）
PLATFORM_COMPARISONS = {
    "防晒冰袖": {
        "category": "户外/服饰配件",
        "platforms": {
            "pinduoduo": {"avg_price": 15.9, "competitors": 180, "search_volume": "高", "trend": "↑320%", "margin": "35%", "recommendation": "⭐⭐⭐ 价格敏感型用户多，走量快"},
            "taobao": {"avg_price": 29.9, "competitors": 420, "search_volume": "很高", "trend": "↑280%", "margin": "45%", "recommendation": "⭐⭐ 竞争激烈但客单价高，需差异化"},
            "douyin": {"avg_price": 39.9, "competitors": 95, "search_volume": "极高", "trend": "↑450%", "margin": "55%", "recommendation": "⭐⭐⭐ 内容电商红利期，达人带货爆发"},
        },
        "best_platform": "douyin",
        "strategy": "抖音首发（高毛利+达人带货）→ 拼多多走量 → 淘宝维持品牌形象",
    },
    "大容量运动水杯": {
        "category": "户外/家居",
        "platforms": {
            "pinduoduo": {"avg_price": 19.9, "competitors": 280, "search_volume": "中", "trend": "↑180%", "margin": "30%", "recommendation": "⭐⭐ 低价量大，利润薄"},
            "taobao": {"avg_price": 49.9, "competitors": 350, "search_volume": "高", "trend": "↑245%", "margin": "50%", "recommendation": "⭐⭐⭐ 中高端用户匹配，利润空间好"},
            "douyin": {"avg_price": 59.9, "competitors": 72, "search_volume": "高", "trend": "↑310%", "margin": "55%", "recommendation": "⭐⭐ 健身/户外达人种草效果好"},
        },
        "best_platform": "taobao",
        "strategy": "淘宝主攻（品质用户+高利润）→ 抖音达人分销 → 拼多多基础款走量",
    },
    "国风新中式连衣裙": {
        "category": "女装",
        "platforms": {
            "pinduoduo": {"avg_price": 59.9, "competitors": 110, "search_volume": "中", "trend": "↑120%", "margin": "38%", "recommendation": "⭐⭐ 价格偏高，拼多多用户接受度低"},
            "taobao": {"avg_price": 129.0, "competitors": 280, "search_volume": "高", "trend": "↑180%", "margin": "52%", "recommendation": "⭐⭐⭐ 核心战场，需差异化解锁流量"},
            "douyin": {"avg_price": 159.0, "competitors": 45, "search_volume": "很高", "trend": "↑350%", "margin": "60%", "recommendation": "⭐⭐⭐ 新中式内容种草爆发，达人直播带货"},
        },
        "best_platform": "douyin",
        "strategy": "抖音首发（内容种草+高溢价）→ 淘宝铺货 → 拼多多观望再决定",
    },
}


def cmd_compare(args):
    keyword = args.keyword or ""
    # 模糊匹配
    matched = None
    for k, v in PLATFORM_COMPARISONS.items():
        if keyword in k or k in keyword:
            matched = v
            matched["keyword"] = k
            break

    if not matched:
        print(json.dumps({"error": f"未找到「{keyword}」的跨平台数据，可搜索：{list(PLATFORM_COMPARISONS.keys())}"}, ensure_ascii=False))
        return

    print(json.dumps(matched, ensure_ascii=False))


def cmd_platform_recommend(args):
    """根据品类推荐最适合的平台"""
    recommendations = []
    for name, data in PLATFORM_COMPARISONS.items():
        recommendations.append({
            "category": name,
            "best_platform": data["best_platform"],
            "strategy": data["strategy"],
        })
    print(json.dumps({"categories": recommendations}, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="跨平台选品对比")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("compare"); s.add_argument("--keyword", required=True)
    sp.add_parser("recommend")

    a = p.parse_args()
    {"compare": cmd_compare, "recommend": cmd_platform_recommend}[a.cmd](a)
