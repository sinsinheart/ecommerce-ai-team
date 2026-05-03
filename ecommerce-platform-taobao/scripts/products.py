#!/usr/bin/env python3
"""淘宝/天猫 — 商品管理（读取/修改/上下架/库存/竞品调研）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import call_api


def cmd_get(args):
    r = call_api(args.shop_id, "taobao.item.get", {
        "fields": "num_iid,title,price,desc,pic_url,detail_url,cid,props_name,sku_properties,seller_cids,nick,delist_time,stuff_status,sell_point,item_weight,has_discount,is_virtual,has_showcase,modified,approve_status",
        "num_iid": args.num_iid,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_list(args):
    r = call_api(args.shop_id, "taobao.items.onsale.get", {
        "fields": "num_iid,title,price,pic_url,has_discount,modified,volume",
        "page_no": args.page or 1,
        "page_size": args.size or 20,
        "order_by": args.order or "modified:desc",
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_update(args):
    params = {"num_iid": args.num_iid}
    if args.title: params["title"] = args.title
    if args.desc: params["desc"] = args.desc
    if args.price: params["price"] = args.price
    if args.seller_cids: params["seller_cids"] = args.seller_cids
    if args.stuff_status: params["stuff_status"] = args.stuff_status
    r = call_api(args.shop_id, "taobao.item.update", params)
    print(json.dumps(r, ensure_ascii=False))


def cmd_offline(args):
    r = call_api(args.shop_id, "taobao.item.update.delisting", {"num_iid": args.num_iid})
    print(json.dumps(r, ensure_ascii=False))


def cmd_online(args):
    r = call_api(args.shop_id, "taobao.item.update.listing", {"num_iid": args.num_iid, "num": args.num or 999})
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="淘宝商品管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("get"); s.add_argument("--shop-id", required=True); s.add_argument("--num-iid", required=True)
    s = sp.add_parser("list"); s.add_argument("--shop-id", required=True); s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--order")
    s = sp.add_parser("update"); s.add_argument("--shop-id", required=True); s.add_argument("--num-iid", required=True)
    s.add_argument("--title"); s.add_argument("--desc"); s.add_argument("--price"); s.add_argument("--seller-cids"); s.add_argument("--stuff-status")
    s = sp.add_parser("offline"); s.add_argument("--shop-id", required=True); s.add_argument("--num-iid", required=True)
    s = sp.add_parser("online"); s.add_argument("--shop-id", required=True); s.add_argument("--num-iid", required=True); s.add_argument("--num", type=int)

    a = p.parse_args()
    {"get": cmd_get, "list": cmd_list, "update": cmd_update, "offline": cmd_offline, "online": cmd_online}[a.cmd](a)
