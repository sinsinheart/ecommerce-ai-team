#!/usr/bin/env python3
"""
跨平台数据聚合看板
统一展示拼多多/淘宝/抖音三平台核心运营数据
"""

import json
import argparse
import os
import sys
from datetime import datetime

PLATFORM_SCRIPTS = {
    "pinduoduo": {
        "name": "拼多多",
        "emoji": "🔵",
        "script_dir": os.path.join(os.path.dirname(__file__), "..", "..", "ecommerce-platform-pinduoduo", "scripts"),
    },
    "taobao": {
        "name": "淘宝/天猫",
        "emoji": "🟠",
        "script_dir": os.path.join(os.path.dirname(__file__), "..", "..", "ecommerce-platform-taobao", "scripts"),
    },
    "douyin": {
        "name": "抖音小店",
        "emoji": "⚫",
        "script_dir": os.path.join(os.path.dirname(__file__), "..", "..", "ecommerce-platform-douyin", "scripts"),
    },
}

# 模拟店铺数据（演示用，实际接入后从脚本获取）
DEMO_SHOPS = {
    "pinduoduo": {
        "shop_name": "潮流服饰旗舰店",
        "shop_id": "pdd001",
        "metrics": {
            "visitors": 1847, "pageviews": 5928,
            "orders": 86, "revenue": 4837.00,
            "conversion": 4.66, "avg_order": 56.24,
            "dsr": 4.5, "negative_rate": 4.2,
            "refund_count": 5,
        },
        "alerts": [
            {"level": "yellow", "msg": "差评率 4.2% > 3%"},
            {"level": "red", "msg": "韩版宽松T恤差评12条"},
        ],
        "top_products": [
            {"rank": 1, "name": "韩版宽松T恤", "visitors": 352, "orders": 23, "conversion": 6.53},
            {"rank": 2, "name": "冰丝防晒冰袖", "visitors": 278, "orders": 19, "conversion": 6.83},
            {"rank": 3, "name": "修身牛仔裤", "visitors": 194, "orders": 11, "conversion": 5.67},
        ],
    },
    "taobao": {
        "shop_name": "潮流服饰旗舰店",
        "shop_id": "tb001",
        "metrics": {
            "visitors": 2105, "pageviews": 6430,
            "orders": 95, "revenue": 6120.00,
            "conversion": 4.51, "avg_order": 64.42,
            "dsr": 4.7, "negative_rate": 3.1,
            "refund_count": 8,
        },
        "alerts": [
            {"level": "yellow", "msg": "差评率 3.1% > 3%"},
        ],
        "top_products": [
            {"rank": 1, "name": "韩版宽松T恤", "visitors": 412, "orders": 28, "conversion": 6.80},
            {"rank": 2, "name": "冰丝防晒冰袖", "visitors": 310, "orders": 22, "conversion": 7.10},
            {"rank": 3, "name": "国风新中式连衣裙", "visitors": 255, "orders": 14, "conversion": 5.49},
        ],
    },
    "douyin": {
        "shop_name": "潮流服饰旗舰店",
        "shop_id": "dy001",
        "metrics": {
            "visitors": 5620, "pageviews": 12800,
            "orders": 156, "revenue": 8736.00,
            "conversion": 2.78, "avg_order": 56.00,
            "dsr": 4.6, "negative_rate": 5.1,
            "refund_count": 18,
        },
        "alerts": [
            {"level": "red", "msg": "差评率 5.1% > 3%（内容电商差评率高）"},
            {"level": "yellow", "msg": "退款率偏高 11.5%"},
        ],
        "top_products": [
            {"rank": 1, "name": "冰丝防晒冰袖", "visitors": 1850, "orders": 58, "conversion": 3.14},
            {"rank": 2, "name": "大容量运动水杯", "visitors": 920, "orders": 32, "conversion": 3.48},
            {"rank": 3, "name": "堆堆袜套装", "visitors": 680, "orders": 25, "conversion": 3.68},
        ],
    },
}


def get_shop_data(platform_key, use_demo=True):
    """获取平台店铺数据，优先使用真实数据"""
    if use_demo:
        return DEMO_SHOPS.get(platform_key)
    # TODO: 实际环境中调用各平台脚本获取真实数据
    return DEMO_SHOPS.get(platform_key)


def cmd_dashboard(args):
    """多平台数据看板"""
    platform = args.platform or "all"
    use_demo = args.demo or False

    platforms_to_show = list(PLATFORM_SCRIPTS.keys()) if platform == "all" else [platform]
    shops_data = []
    total_visitors = total_orders = 0
    total_revenue = 0.0
    all_alerts = []

    for plat in platforms_to_show:
        if plat not in PLATFORM_SCRIPTS:
            continue
        data = get_shop_data(plat, use_demo)
        if data:
            data["platform_key"] = plat
            shops_data.append(data)
            m = data["metrics"]
            total_visitors += m["visitors"]
            total_orders += m["orders"]
            total_revenue += m["revenue"]
            all_alerts.extend(data.get("alerts", []))

    result = {
        "platform": platform,
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "shop_count": len(shops_data),
        "shops": shops_data,
        "aggregate": {
            "total_visitors": total_visitors,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "total_conversion": round(total_orders / total_visitors * 100, 2) if total_visitors > 0 else 0,
            "total_avg_order": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
        },
        "alerts": all_alerts,
    }
    print(json.dumps(result, ensure_ascii=False))


def cmd_switch(args):
    """切换平台视图"""
    platform = args.platform
    if platform not in list(PLATFORM_SCRIPTS.keys()) + ["all"]:
        print(json.dumps({"error": f"未知平台: {platform}，可选: {list(PLATFORM_SCRIPTS.keys()) + ['all']}"}))
        return
    print(json.dumps({
        "action": "switch",
        "platform": platform,
        "platform_name": PLATFORM_SCRIPTS.get(platform, {}).get("name", "全平台"),
        "emoji": PLATFORM_SCRIPTS.get(platform, {}).get("emoji", "🌐"),
        "message": f"已切换到 {'全平台聚合视图' if platform == 'all' else PLATFORM_SCRIPTS[platform]['name']}",
    }, ensure_ascii=False))


def cmd_alerts(args):
    """跨平台异常聚合预警"""
    platforms = list(PLATFORM_SCRIPTS.keys())
    all_alerts = []
    for plat in platforms:
        data = get_shop_data(plat, True)
        if data:
            for alert in data.get("alerts", []):
                alert["platform"] = plat
                alert["platform_name"] = PLATFORM_SCRIPTS[plat]["name"]
                all_alerts.append(alert)

    red = [a for a in all_alerts if a["level"] == "red"]
    yellow = [a for a in all_alerts if a["level"] == "yellow"]

    result = {
        "total_alerts": len(all_alerts),
        "critical": len(red),
        "warning": len(yellow),
        "alerts": all_alerts,
    }
    print(json.dumps(result, ensure_ascii=False))


def cmd_compare(args):
    """跨平台指标对比"""
    metric = args.metric or "all"
    platforms = list(PLATFORM_SCRIPTS.keys())
    comparison = {}

    for plat in platforms:
        data = get_shop_data(plat, True)
        if data:
            m = data["metrics"]
            comparison[plat] = {
                "platform_name": PLATFORM_SCRIPTS[plat]["name"],
                "emoji": PLATFORM_SCRIPTS[plat]["emoji"],
                "visitors": m["visitors"],
                "orders": m["orders"],
                "revenue": m["revenue"],
                "conversion": m["conversion"],
                "avg_order": m["avg_order"],
                "dsr": m["dsr"],
                "negative_rate": m["negative_rate"],
            }

    # 计算排名
    for k in ["visitors", "orders", "revenue", "conversion", "dsr"]:
        ranked = sorted(comparison.items(), key=lambda x: x[1][k], reverse=True)
        for i, (plat, _) in enumerate(ranked):
            comparison[plat][f"{k}_rank"] = i + 1

    print(json.dumps({"metric": metric, "comparison": comparison}, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="跨平台数据聚合看板")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("dashboard"); s.add_argument("--platform", choices=["pinduoduo", "taobao", "douyin", "all"]); s.add_argument("--date"); s.add_argument("--demo", type=bool, default=True)
    s = sp.add_parser("switch"); s.add_argument("--platform", required=True, choices=["pinduoduo", "taobao", "douyin", "all"])
    sp.add_parser("alerts")
    s = sp.add_parser("compare"); s.add_argument("--metric", default="all")

    a = p.parse_args()
    {"dashboard": cmd_dashboard, "switch": cmd_switch, "alerts": cmd_alerts, "compare": cmd_compare}[a.cmd](a)
