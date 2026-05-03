#!/usr/bin/env python3
"""抖音小店 — 订单管理与物流跟踪"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import api_call


def cmd_list(args):
    r = api_call(args.shop_id, "/order/search", {
        "page": args.page or 1,
        "size": args.size or 20,
        "start_time": args.start or None,
        "end_time": args.end or None,
        "order_status": args.status or None,
        "order_by": "create_time",
        "is_desc": 1,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_detail(args):
    r = api_call(args.shop_id, "/order/getOrderDetail", {"order_id": args.order_id})
    print(json.dumps(r, ensure_ascii=False))


def cmd_ship(args):
    """发货"""
    r = api_call(args.shop_id, "/order/logisticsAdd", {
        "order_id": args.order_id,
        "logistics_code": args.logistics_code,
        "company": args.company or "",
        "company_code": args.company_code or "",
    })
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="抖音小店订单管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("list"); s.add_argument("--shop-id", required=True)
    s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--status"); s.add_argument("--start"); s.add_argument("--end")
    s = sp.add_parser("detail"); s.add_argument("--shop-id", required=True); s.add_argument("--order-id", required=True)
    s = sp.add_parser("ship"); s.add_argument("--shop-id", required=True); s.add_argument("--order-id", required=True)
    s.add_argument("--logistics-code", required=True); s.add_argument("--company"); s.add_argument("--company-code")

    a = p.parse_args()
    {"list": cmd_list, "detail": cmd_detail, "ship": cmd_ship}[a.cmd](a)
