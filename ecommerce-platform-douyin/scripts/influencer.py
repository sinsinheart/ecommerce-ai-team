#!/usr/bin/env python3
"""抖音小店 — 达人带货管理（达人数据/商品分销/佣金管理）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import api_call


def cmd_kol_products(args):
    """获取达人带货商品列表"""
    r = api_call(args.shop_id, "/kol/product/list", {
        "page": args.page or 1,
        "size": args.size or 20,
        "product_id": args.product_id or None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_distribute(args):
    """设置商品分销计划"""
    r = api_call(args.shop_id, "/product/distribute", {
        "product_id": args.product_id,
        "kol_plan": json.loads(args.kol_plan) if args.kol_plan else None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_authorize(args):
    """获取达人授权信息"""
    r = api_call(args.shop_id, "/alliance/getAuthorizeInfo", {
        "author_id": args.author_id,
    })
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="抖音小店达人带货管理")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("kol-products"); s.add_argument("--shop-id", required=True)
    s.add_argument("--product-id"); s.add_argument("--page", type=int); s.add_argument("--size", type=int)
    s = sp.add_parser("distribute"); s.add_argument("--shop-id", required=True); s.add_argument("--product-id", required=True); s.add_argument("--kol-plan")
    s = sp.add_parser("authorize"); s.add_argument("--shop-id", required=True); s.add_argument("--author-id", required=True)

    a = p.parse_args()
    {"kol-products": cmd_kol_products, "distribute": cmd_distribute, "authorize": cmd_authorize}[a.cmd](a)
