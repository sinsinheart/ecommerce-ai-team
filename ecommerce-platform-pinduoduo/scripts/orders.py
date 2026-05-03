"""
拼多多订单管理API
支持订单列表、详情、物流查询

Usage:
    python orders.py list --shop-id <id> [--status pending|shipped|completed] [--days 7]
    python orders.py detail --shop-id <id> --order-sn <sn>
    python orders.py logistics --shop-id <id> --order-sn <sn>
    python orders.py summary --shop-id <id> [--days 1]
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from auth import call_api


def cmd_list(args):
    """订单列表"""
    params = {"page": "1", "page_size": "50"}
    if args.status:
        status_map = {
            "pending": "1",   # 待发货
            "shipped": "2",   # 已发货
            "received": "3",  # 已签收
            "completed": "4", # 已完成
        }
        params["order_status"] = status_map.get(args.status, args.status)

    result = call_api(args.shop_id, "pdd.order.list.get", params)

    if "order_list" in result:
        orders = result["order_list"]
        cutoff = datetime.now() - timedelta(days=args.days) if args.days else None

        filtered = []
        for o in orders:
            order_time = o.get("order_time", "")
            if cutoff and order_time:
                try:
                    ot = datetime.fromisoformat(order_time)
                    if ot < cutoff:
                        continue
                except:
                    pass
            filtered.append(o)

        print(f"共 {len(filtered)} 个订单：\n")
        print(f"{'订单号':<25} {'商品':<20} {'金额':<10} {'状态':<8} {'时间'}")
        print("-" * 90)
        for o in filtered:
            sn = str(o.get("order_sn", ""))
            goods = o.get("goods_name", "")[:18]
            amount = f"¥{o.get('order_amount', 0)/100:.2f}"
            status_map = {"1": "待发货", "2": "已发货", "3": "已签收", "4": "已完成"}
            status = status_map.get(str(o.get("order_status", "")), "未知")
            time_str = o.get("order_time", "-")[:10]
            print(f"{sn:<25} {goods:<20} {amount:<10} {status:<8} {time_str}")
    else:
        print("未获取到订单数据")


def cmd_detail(args):
    """订单详情"""
    result = call_api(args.shop_id, "pdd.order.detail.get",
                      {"order_sn": str(args.order_sn)})

    if "order_detail" in result:
        d = result["order_detail"]
        print(f"=== 订单详情 ===")
        print(f"  订单号: {d.get('order_sn')}")
        print(f"  商品: {d.get('goods_name')}")
        print(f"  金额: ¥{d.get('order_amount', 0)/100:.2f}")
        print(f"  数量: {d.get('goods_count', 1)}")
        print(f"  买家: {d.get('buyer_name', '匿名')}")
        print(f"  收货地址: {d.get('receiver_province', '')} {d.get('receiver_city', '')} {d.get('receiver_district', '')} {d.get('receiver_address', '')}")
        print(f"  手机: {d.get('receiver_phone', '')}")
        print(f"  下单时间: {d.get('order_time')}")
        print(f"  支付时间: {d.get('pay_time', '-')}")
        print(f"  发货时间: {d.get('ship_time', '-')}")
        print(f"  状态: {d.get('order_status_desc', '')}")
    else:
        print("未找到订单")


def cmd_logistics(args):
    """查询物流"""
    result = call_api(args.shop_id, "pdd.logistics.track.get",
                      {"order_sn": str(args.order_sn)})

    if "logistics" in result:
        log = result["logistics"]
        print(f"=== 物流信息 ===")
        print(f"  物流公司: {log.get('company', '未知')}")
        print(f"  运单号: {log.get('tracking_number', '未知')}")
        print(f"  当前状态: {log.get('status_desc', '未知')}")
        print(f"\n  物流轨迹：")
        for node in log.get("nodes", []):
            print(f"    {node.get('time', '')}  {node.get('desc', '')}")

        # 异常检测
        status = log.get("status", "")
        if status in ["problem", "returned", "lost"]:
            print(f"\n  ⚠️ 物流异常！状态: {status}")
            print(f"  建议: 主动联系买家安抚，通知物流公司核实")
    else:
        print("未找到物流信息")


def cmd_summary(args):
    """订单概览"""
    result = call_api(args.shop_id, "pdd.order.statistics.get",
                      {"days": str(args.days)})

    if "statistics" in result:
        s = result["statistics"]
        print(f"=== 订单概览（{args.days}天）===")
        print(f"  总订单数: {s.get('total_orders', 0)}")
        print(f"  总成交额: ¥{s.get('total_amount', 0)/100:.2f}")
        print(f"  客单价: ¥{s.get('avg_order_amount', 0)/100:.2f}")
        print(f"  待发货: {s.get('pending_ship', 0)}单")
        print(f"  已发货: {s.get('shipped', 0)}单")
        print(f"  已完成: {s.get('completed', 0)}单")
        print(f"  退款中: {s.get('refunding', 0)}单")

        pending = s.get("pending_ship", 0)
        if pending > 0:
            overdue_hours = s.get("pending_overdue_hours", 0)
            if overdue_hours > 0:
                print(f"\n  ⚠️ {pending}单待发货中，{overdue_hours}单超时，请尽快处理！")
    else:
        # 降级：从订单列表统计
        result2 = call_api(args.shop_id, "pdd.order.list.get", {"page_size": "100"})
        if "order_list" in result2:
            orders = result2["order_list"]
            total = len(orders)
            total_amount = sum(o.get("order_amount", 0) for o in orders) / 100
            pending = sum(1 for o in orders if str(o.get("order_status")) == "1")
            print(f"=== 订单概览（近似统计）===")
            print(f"  总订单数: {total}")
            print(f"  总成交额: ¥{total_amount:.2f}")
            print(f"  待发货: {pending}单")


def main():
    parser = argparse.ArgumentParser(description="拼多多订单管理")
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="订单列表")
    p_list.add_argument("--shop-id", required=True)
    p_list.add_argument("--status", help="pending|shipped|received|completed")
    p_list.add_argument("--days", type=int, default=7)

    # detail
    p_detail = sub.add_parser("detail", help="订单详情")
    p_detail.add_argument("--shop-id", required=True)
    p_detail.add_argument("--order-sn", required=True)

    # logistics
    p_log = sub.add_parser("logistics", help="物流查询")
    p_log.add_argument("--shop-id", required=True)
    p_log.add_argument("--order-sn", required=True)

    # summary
    p_sum = sub.add_parser("summary", help="订单概览")
    p_sum.add_argument("--shop-id", required=True)
    p_sum.add_argument("--days", type=int, default=1)

    args = parser.parse_args()

    commands = {
        "list": cmd_list, "detail": cmd_detail, "logistics": cmd_logistics,
        "summary": cmd_summary,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
