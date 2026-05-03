#!/usr/bin/env python3
"""淘宝/天猫 — 售后管理（退款审核/退货处理）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import call_api


def cmd_list(args):
    """获取退款列表"""
    params = {
        "fields": "refund_id,tid,title,price,refund_fee,num,status,created,modified,reason,desc,good_return_time,company_name,sid,shipping_type,order_status,has_good_return",
        "page_no": args.page or 1,
        "page_size": args.size or 20,
    }
    if args.status: params["status"] = args.status
    if args.start: params["start_created"] = args.start
    if args.end: params["end_created"] = args.end
    r = call_api(args.shop_id, "taobao.refunds.receive.get", params)
    print(json.dumps(r, ensure_ascii=False))


def cmd_detail(args):
    r = call_api(args.shop_id, "taobao.refund.get", {
        "fields": "refund_id,tid,title,price,refund_fee,num,status,created,modified,reason,desc,oid,good_return_time,company_name,sid,shipping_type,address,buyer_nick",
        "refund_id": args.refund_id,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_audit(args):
    """审核退款/退货"""
    if args.action == "approve":
        r = call_api(args.shop_id, "taobao.refund.agree", {
            "refund_id": args.refund_id,
            "refund_phase": args.phase or "onsale",
        })
    elif args.action == "refuse":
        r = call_api(args.shop_id, "taobao.refund.refuse", {
            "refund_id": args.refund_id,
            "refund_phase": args.phase or "onsale",
            "refund_version": args.version or "1",
            "refuse_message": args.reason or "平台规则不符",
        })
    else:
        r = {"error": f"未知操作: {args.action}"}
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="淘宝售后管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("list"); s.add_argument("--shop-id", required=True)
    s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--status"); s.add_argument("--start"); s.add_argument("--end")
    s = sp.add_parser("detail"); s.add_argument("--shop-id", required=True); s.add_argument("--refund-id", required=True)
    s = sp.add_parser("audit"); s.add_argument("--shop-id", required=True); s.add_argument("--refund-id", required=True)
    s.add_argument("--action", required=True, choices=["approve", "refuse"]); s.add_argument("--phase"); s.add_argument("--reason"); s.add_argument("--version")

    a = p.parse_args()
    {"list": cmd_list, "detail": cmd_detail, "audit": cmd_audit}[a.cmd](a)
