#!/usr/bin/env python3
"""抖音小店 — 评价管理（抓取/追评/回复/申诉）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import api_call


def cmd_fetch(args):
    """抓取评价"""
    r = api_call(args.shop_id, "/product/getComment", {
        "product_id": args.product_id,
        "page": args.page or 1,
        "size": args.size or 20,
        "score": int(args.rating) if args.rating else None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_reply(args):
    """回复评价"""
    r = api_call(args.shop_id, "/product/replyComment", {
        "comment_id": args.comment_id,
        "content": args.content,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_summary(args):
    """评价摘要统计"""
    results = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for rating in ["1", "2", "3", "4", "5"]:
        r = api_call(args.shop_id, "/product/getComment", {
            "product_id": args.product_id,
            "page": 1, "size": 100, "score": int(rating),
        })
        results[rating] = r.get("data", {}).get("total", 0) if isinstance(r, dict) else 0

    total = sum(results.values())
    bad = results["1"] + results["2"] + results["3"]
    print(json.dumps({
        "product_id": args.product_id,
        "total_rate_count": total,
        "negative_count": bad,
        "negative_rate": f"{bad/total*100:.1f}%" if total > 0 else "0%",
        "distribution": results,
    }, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="抖音小店评价管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("fetch"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True)
    s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--rating")
    s = sp.add_parser("reply"); s.add_argument("--shop-id", required=True); s.add_argument("--comment-id", required=True); s.add_argument("--content", required=True)
    s = sp.add_parser("summary"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True)

    a = p.parse_args()
    {"fetch": cmd_fetch, "reply": cmd_reply, "summary": cmd_summary}[a.cmd](a)
