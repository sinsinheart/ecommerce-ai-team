"""
拼多多售后处理API
支持退款审核、退货物流追踪、纠纷处理

Usage:
    python aftersales.py list --shop-id <id> [--status pending|approved|rejected]
    python aftersales.py audit --shop-id <id> --refund-id <id> --action (approve|reject) [--reason "不符合退货条件"]
    python aftersales.py detail --shop-id <id> --refund-id <id>
    python aftersales.py logistics --shop-id <id> --refund-id <id>
    python aftersales.py fraud-check --shop-id <id> --refund-id <id>
    python aftersales.py batch-audit --shop-id <id>
    python aftersales.py stats --shop-id <id> [--days 30]
"""

import json
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from auth import call_api, load_json, TOKEN_FILE, SHOP_FILE


# 恶意订单检测规则
FRAUD_RULES = {
    "高频退货": {"max_returns_30d": 3},
    "金额阈值": {"max_auto_amount": 500},
    "异常时段": {"risk_hours": [2, 3, 4, 5]},  # 凌晨2-5点
}


def check_fraud(shop_id, refund_info):
    """检测恶意退款行为"""
    risks = []

    # 检查买家30天退货次数
    buyer_returns = refund_info.get("buyer_returns_30d", 0)
    if buyer_returns >= FRAUD_RULES["高频退货"]["max_returns_30d"]:
        risks.append(f"买家30天退货{buyer_returns}次，超过阈值")

    # 检查金额
    amount = float(refund_info.get("refund_amount", 0)) / 100
    if amount >= FRAUD_RULES["金额阈值"]["max_auto_amount"]:
        risks.append(f"退款金额¥{amount:.2f}超过自动审核限额")

    # 检查申请时间
    apply_hour = None
    apply_time = refund_info.get("apply_time", "")
    if apply_time:
        try:
            apply_hour = datetime.fromisoformat(apply_time).hour
            if apply_hour in FRAUD_RULES["异常时段"]["risk_hours"]:
                risks.append(f"凌晨{apply_hour}点提交申请，异常时间")
        except:
            pass

    # 判断是否需要人工复核
    need_review = len(risks) >= 2 or amount >= FRAUD_RULES["金额阈值"]["max_auto_amount"]

    return {
        "risk_level": "high" if need_review else ("medium" if risks else "low"),
        "risks": risks,
        "need_manual_review": need_review,
    }


def cmd_list(args):
    """售后列表"""
    params = {"page": "1", "page_size": "50"}
    if args.status:
        params["refund_status"] = args.status

    result = call_api(args.shop_id, "pdd.refund.list.get", params)

    if "refund_list" in result:
        refunds = result["refund_list"]
        print(f"{'退款ID':<20} {'商品':<30} {'金额':<10} {'状态':<8} {'申请时间'}")
        print("-" * 100)
        for r in refunds:
            rid = str(r.get("refund_id", ""))
            goods = r.get("goods_name", "")[:28]
            amount = f"¥{r.get('refund_amount', 0)/100:.2f}"
            status_map = {"1": "待审核", "2": "已通过", "3": "已拒绝", "4": "已完成"}
            status = status_map.get(str(r.get("refund_status", "")), "未知")
            time_str = r.get("apply_time", "-")
            print(f"{rid:<20} {goods:<30} {amount:<10} {status:<8} {time_str}")
    else:
        print("无售后申请数据")


def cmd_detail(args):
    """售后详情"""
    result = call_api(args.shop_id, "pdd.refund.detail.get",
                      {"refund_id": str(args.refund_id)})

    if "refund_detail" in result:
        d = result["refund_detail"]
        print(f"=== 售后单详情 ===")
        print(f"  退款ID: {d.get('refund_id')}")
        print(f"  订单号: {d.get('order_sn')}")
        print(f"  商品: {d.get('goods_name')}")
        print(f"  金额: ¥{d.get('refund_amount', 0)/100:.2f}")
        print(f"  原因: {d.get('refund_reason')}")
        print(f"  描述: {d.get('refund_desc', '无')}")
        print(f"  买家: {d.get('buyer_name', '匿名')}")
        print(f"  申请时间: {d.get('apply_time')}")

        fraud = check_fraud(args.shop_id, d)
        print(f"\n  风控评估:")
        print(f"    风险等级: {fraud['risk_level']}")
        if fraud["risks"]:
            for r in fraud["risks"]:
                print(f"    ⚠️ {r}")
        print(f"    建议: {'人工复核' if fraud['need_manual_review'] else '可自动处理'}")
    else:
        print("未找到售后单")


def cmd_audit(args):
    """审核售后申请"""
    fraud = None

    if args.action == "approve":
        # 通过前先做风控检查
        detail = call_api(args.shop_id, "pdd.refund.detail.get",
                          {"refund_id": str(args.refund_id)})
        if "refund_detail" in detail:
            fraud = check_fraud(args.shop_id, detail["refund_detail"])
            if fraud["need_manual_review"] and not args.force:
                print(f"⚠️ 风控拦截！原因：")
                for r in fraud["risks"]:
                    print(f"  - {r}")
                print(f"\n如需强制通过，请加 --force 参数")
                return

        result = call_api(args.shop_id, "pdd.refund.approve",
                          {"refund_id": str(args.refund_id)})
        if "error_response" not in result:
            print(f"退款单 {args.refund_id} 已批准 ✓")
        else:
            print(f"操作失败: {result['error_response'].get('error_msg')}")

    elif args.action == "reject":
        result = call_api(args.shop_id, "pdd.refund.refuse", {
            "refund_id": str(args.refund_id),
            "refuse_reason": args.reason or "不符合退货条件",
        })
        if "error_response" not in result:
            print(f"退款单 {args.refund_id} 已拒绝 ✗")
            print(f"  拒绝原因: {args.reason or '不符合退货条件'}")
        else:
            print(f"操作失败: {result['error_response'].get('error_msg')}")


def cmd_logistics(args):
    """追踪退货物流"""
    result = call_api(args.shop_id, "pdd.refund.logistics.get",
                      {"refund_id": str(args.refund_id)})

    if "logistics" in result:
        log = result["logistics"]
        print(f"=== 退货物流追踪 ===")
        print(f"  物流公司: {log.get('company', '未知')}")
        print(f"  运单号: {log.get('tracking_number', '未知')}")
        print(f"  当前状态: {log.get('status_desc', '未知')}")
        print(f"\n  物流轨迹：")
        for node in log.get("nodes", []):
            print(f"    {node.get('time', '')}  {node.get('desc', '')}")
    else:
        print("未找到物流信息")


def cmd_batch_audit(args):
    """批量自动审核"""
    result = call_api(args.shop_id, "pdd.refund.list.get",
                      {"page": "1", "page_size": "100", "refund_status": "1"})  # 待审核

    if "refund_list" not in result:
        print("无待审核售后单")
        return

    refunds = result["refund_list"]
    approved = 0
    rejected = 0
    manual = 0

    print(f"共 {len(refunds)} 单待审核，正在自动处理...\n")

    for r in refunds:
        rid = r["refund_id"]
        detail = call_api(args.shop_id, "pdd.refund.detail.get", {"refund_id": str(rid)})

        if "refund_detail" not in detail:
            continue

        fraud = check_fraud(args.shop_id, detail["refund_detail"])

        if fraud["need_manual_review"]:
            manual += 1
            print(f"  ⚠️ {rid} → 人工复核（{'; '.join(fraud['risks'])})")
        elif fraud["risk_level"] == "medium":
            # 中等风险，谨慎通过
            call_api(args.shop_id, "pdd.refund.approve", {"refund_id": str(rid)})
            approved += 1
            print(f"  🟡 {rid} → 自动通过（低风险）")
        else:
            call_api(args.shop_id, "pdd.refund.approve", {"refund_id": str(rid)})
            approved += 1
            print(f"  🟢 {rid} → 自动通过")

    print(f"\n处理完成：✅ 自动通过 {approved} | ⚠️ 人工复核 {manual} | ❌ 拒绝 {rejected}")


def cmd_stats(args):
    """售后统计"""
    print(f"=== 售后数据统计（{args.days}天）===")
    # 此处应调用统计接口，仅做示意
    result = call_api(args.shop_id, "pdd.refund.stats.get", {"days": str(args.days)})
    if "stats" in result:
        print(json.dumps(result["stats"], indent=2, ensure_ascii=False))
    else:
        print("  退货率: 待对接API")
        print("  退款率: 待对接API")
        print("  纠纷率: 待对接API")
        print("  自动审核通过率: 待对接API")


def main():
    parser = argparse.ArgumentParser(description="拼多多售后处理")
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="售后列表")
    p_list.add_argument("--shop-id", required=True)
    p_list.add_argument("--status", help="pending|approved|rejected|completed")

    # detail
    p_detail = sub.add_parser("detail", help="售后详情")
    p_detail.add_argument("--shop-id", required=True)
    p_detail.add_argument("--refund-id", required=True)

    # audit
    p_audit = sub.add_parser("audit", help="审核售后")
    p_audit.add_argument("--shop-id", required=True)
    p_audit.add_argument("--refund-id", required=True)
    p_audit.add_argument("--action", required=True, choices=["approve", "reject"])
    p_audit.add_argument("--reason")
    p_audit.add_argument("--force", action="store_true", help="跳过风控强制通过")

    # logistics
    p_log = sub.add_parser("logistics", help="退货物流追踪")
    p_log.add_argument("--shop-id", required=True)
    p_log.add_argument("--refund-id", required=True)

    # fraud-check
    p_fraud = sub.add_parser("fraud-check", help="恶意订单检测")
    p_fraud.add_argument("--shop-id", required=True)
    p_fraud.add_argument("--refund-id", required=True)

    # batch-audit
    p_batch = sub.add_parser("batch-audit", help="批量自动审核")
    p_batch.add_argument("--shop-id", required=True)

    # stats
    p_stats = sub.add_parser("stats", help="售后统计")
    p_stats.add_argument("--shop-id", required=True)
    p_stats.add_argument("--days", type=int, default=30)

    args = parser.parse_args()

    if args.command == "fraud-check":
        result = call_api(args.shop_id, "pdd.refund.detail.get",
                          {"refund_id": str(args.refund_id)})
        if "refund_detail" in result:
            fraud = check_fraud(args.shop_id, result["refund_detail"])
            print(json.dumps(fraud, indent=2, ensure_ascii=False))

    commands = {
        "list": cmd_list, "detail": cmd_detail, "audit": cmd_audit,
        "logistics": cmd_logistics, "batch-audit": cmd_batch_audit, "stats": cmd_stats,
    }

    if args.command in commands:
        commands[args.command](args)
    elif args.command != "fraud-check":
        parser.print_help()


if __name__ == "__main__":
    main()
