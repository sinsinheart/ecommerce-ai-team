#!/usr/bin/env python3
"""淘宝/天猫 — 评价管理（抓取/追评/问大家/解释回复）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import call_api


def cmd_fetch(args):
    """抓取指定商品评价"""
    r = call_api(args.shop_id, "taobao.traderates.get", {
        "fields": "tid,oid,role,nick,item_title,item_price,content,reply,created,rated_nick,num_iid,valid_score",
        "rate_type": "get",
        "role": "buyer",
        "result": "bad" if args.rating and args.rating in ["1", "2", "3"] else "",
        "page_no": args.page or 1,
        "page_size": args.size or 20,
        "start_date": args.start or "",
        "end_date": args.end or "",
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_reply(args):
    """卖家回复评价"""
    r = call_api(args.shop_id, "taobao.traderate.list.add", {
        "tid": args.tid,
        "oid": args.oid,
        "result": "good",
        "role": "seller",
        "content": args.content,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_summary(args):
    """评价摘要统计（差评/中评/好评分级统计）"""
    all_rates = []
    for rating in ["1", "2", "3", "4", "5"]:
        r = call_api(args.shop_id, "taobao.traderates.get", {
            "fields": "tid,oid,content,created,num_iid,valid_score",
            "rate_type": "get",
            "role": "buyer",
            "result": "bad" if rating in ["1", "2", "3"] else "good",
            "page_no": 1,
            "page_size": 100,
            "start_date": args.start or "",
            "end_date": args.end or "",
        })
        all_rates.append({"rating": rating, "data": r})

    # 统计
    total = sum(len(item.get("data", {}).get("trade_rates", {}).get("trade_rate", [])) for item in all_rates)
    bad_count = sum(len(item.get("data", {}).get("trade_rates", {}).get("trade_rate", [])) for item in all_rates[:3])
    print(json.dumps({
        "total_rate_count": total,
        "negative_count": bad_count,
        "negative_rate": f"{bad_count / total * 100:.1f}%" if total > 0 else "0%",
        "detail": all_rates,
    }, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="淘宝评价管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("fetch"); s.add_argument("--shop-id", required=True)
    s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--rating"); s.add_argument("--start"); s.add_argument("--end")
    s = sp.add_parser("reply"); s.add_argument("--shop-id", required=True); s.add_argument("--tid", required=True); s.add_argument("--oid", required=True); s.add_argument("--content", required=True)
    s = sp.add_parser("summary"); s.add_argument("--shop-id", required=True); s.add_argument("--start"); s.add_argument("--end")

    a = p.parse_args()
    {"fetch": cmd_fetch, "reply": cmd_reply, "summary": cmd_summary}[a.cmd](a)
