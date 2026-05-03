#!/usr/bin/env python3
"""抖音小店 — 商品管理（读取/修改/上下架/库存/达人分销）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import api_call


def cmd_detail(args):
    r = api_call(args.shop_id, "/product/detail", {"product_id": args.product_id})
    print(json.dumps(r, ensure_ascii=False))


def cmd_list(args):
    r = api_call(args.shop_id, "/product/listV2", {
        "page": args.page or 1,
        "size": args.size or 20,
        "status": args.status or None,
        "check_status": args.check_status or None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_update(args):
    params = {"product_id": args.product_id}
    if args.title: params["title"] = args.title
    if args.desc: params["description"] = args.desc
    if args.price is not None: params["price"] = int(float(args.price) * 100)  # 分
    if args.extra: params["extra"] = args.extra
    r = api_call(args.shop_id, "/product/editV2", params)
    print(json.dumps(r, ensure_ascii=False))


def cmd_create(args):
    r = api_call(args.shop_id, "/product/addV2", {
        "name": args.name,
        "pic": args.pic or "",
        "description": args.desc or "",
        "market_price": int(float(args.market_price or args.price) * 100),
        "discount_price": int(float(args.price) * 100),
        "first_cid": args.first_cid,
        "second_cid": args.second_cid or "",
        "third_cid": args.third_cid or "",
        "spec_info": json.loads(args.spec_info) if args.spec_info else None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_offline(args):
    r = api_call(args.shop_id, "/product/setOffline", {"product_id": args.product_id})
    print(json.dumps(r, ensure_ascii=False))


def cmd_online(args):
    r = api_call(args.shop_id, "/product/setOnline", {"product_id": args.product_id})
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="抖音小店商品管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("detail"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True)
    s = sp.add_parser("list"); s.add_argument("--shop-id", required=True); s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--status"); s.add_argument("--check-status")
    s = sp.add_parser("update"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True)
    s.add_argument("--title"); s.add_argument("--desc"); s.add_argument("--price"); s.add_argument("--extra")
    s = sp.add_parser("create"); s.add_argument("--shop-id", required=True); s.add_argument("--name", required=True)
    s.add_argument("--price", required=True); s.add_argument("--first-cid", required=True); s.add_argument("--pic"); s.add_argument("--desc")
    s.add_argument("--market-price"); s.add_argument("--second-cid"); s.add_argument("--third-cid"); s.add_argument("--spec-info")
    s = sp.add_parser("offline"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True)
    s = sp.add_parser("online"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True)

    a = p.parse_args()
    {"detail": cmd_detail, "list": cmd_list, "update": cmd_update, "create": cmd_create, "offline": cmd_offline, "online": cmd_online}[a.cmd](a)
