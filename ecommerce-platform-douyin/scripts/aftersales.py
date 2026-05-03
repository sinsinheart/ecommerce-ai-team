#!/usr/bin/env python3
"""抖音小店 — 售后管理（退款/退货/仲裁/商家主动退款）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import api_call


def cmd_list(args):
    r = api_call(args.shop_id, "/refund/search", {
        "page": args.page or 1,
        "size": args.size or 20,
        "start_time": args.start or None,
        "end_time": args.end or None,
        "type": args.type or None,  # 0全部 1仅退款 2退货退款
        "status": args.status or None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_detail(args):
    r = api_call(args.shop_id, "/refund/getDetail", {"refund_id": args.refund_id})
    print(json.dumps(r, ensure_ascii=False))


def cmd_audit(args):
    """审核售后"""
    action_map = {"approve": 1, "refuse": 2, "arbitrate": 3}
    r = api_call(args.shop_id, "/refund/process", {
        "refund_id": args.refund_id,
        "action": action_map.get(args.action, 1),
        "message": args.reason or "",
        "evidence": args.evidence or "",
    })
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="抖音小店售后管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("list"); s.add_argument("--shop-id", required=True)
    s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--type"); s.add_argument("--status"); s.add_argument("--start"); s.add_argument("--end")
    s = sp.add_parser("detail"); s.add_argument("--shop-id", required=True); s.add_argument("--refund-id", required=True)
    s = sp.add_parser("audit"); s.add_argument("--shop-id", required=True); s.add_argument("--refund-id", required=True)
    s.add_argument("--action", required=True, choices=["approve", "refuse", "arbitrate"]); s.add_argument("--reason"); s.add_argument("--evidence")

    a = p.parse_args()
    {"list": cmd_list, "detail": cmd_detail, "audit": cmd_audit}[a.cmd](a)
