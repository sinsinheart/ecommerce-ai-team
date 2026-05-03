#!/usr/bin/env python3
"""淘宝/天猫 — 订单管理与物流跟踪"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import call_api


def cmd_list(args):
    """获取卖家已卖出订单列表"""
    params = {
        "fields": "tid,status,payment,total_fee,post_fee,created,modified,receiver_name,receiver_mobile,buyer_nick,title,type,num,price,num_iid,pic_path,seller_rate,buyer_rate",
        "page_no": args.page or 1,
        "page_size": args.size or 20,
    }
    if args.status: params["status"] = args.status
    if args.start: params["start_created"] = args.start
    if args.end: params["end_created"] = args.end
    r = call_api(args.shop_id, "taobao.trades.sold.get", params)
    print(json.dumps(r, ensure_ascii=False))


def cmd_detail(args):
    r = call_api(args.shop_id, "taobao.trade.get", {
        "fields": "tid,status,payment,total_fee,post_fee,created,modified,receiver_name,receiver_mobile,receiver_state,receiver_city,receiver_district,receiver_address,buyer_nick,buyer_message,orders.title,orders.num,orders.price,orders.num_iid,orders.pic_path,orders.sku_properties_name,orders.refund_status",
        "tid": args.tid,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_logistics(args):
    r = call_api(args.shop_id, "taobao.logistics.trace.search", {
        "tid": args.tid,
        "seller_ip": "127.0.0.1",
    })
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="淘宝订单管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("list"); s.add_argument("--shop-id", required=True)
    s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--status"); s.add_argument("--start"); s.add_argument("--end")
    s = sp.add_parser("detail"); s.add_argument("--shop-id", required=True); s.add_argument("--tid", required=True)
    s = sp.add_parser("logistics"); s.add_argument("--shop-id", required=True); s.add_argument("--tid", required=True)

    a = p.parse_args()
    {"list": cmd_list, "detail": cmd_detail, "logistics": cmd_logistics}[a.cmd](a)
