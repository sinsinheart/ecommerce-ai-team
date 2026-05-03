"""
拼多多商品管理API
支持商品读取、修改、上下架、库存同步等操作

Usage:
    python products.py list --shop-id <id> [--page 1] [--page-size 20]
    python products.py detail --shop-id <id> --goods-id <id>
    python products.py update --shop-id <id> --goods-id <id> --title "新标题"
    python products.py update --shop-id <id> --goods-id <id> --description "新详情"
    python products.py stock --shop-id <id> --goods-id <id> --sku-id <id> --quantity 100
    python products.py listing --shop-id <id> --goods-id <id> --action (on|off)
    python products.py search-hot --keyword "连衣裙" [--top 20]
    python products.py low-traffic --shop-id <id> [--days 7] [--threshold 100]
"""

import json
import sys
import argparse
import time
from pathlib import Path

# 导入认证模块
sys.path.insert(0, str(Path(__file__).parent))
from auth import call_api, load_json, TOKEN_FILE, SHOP_FILE


def cmd_list(args):
    """获取商品列表"""
    params = {
        "page": str(args.page),
        "page_size": str(args.page_size),
    }
    if args.status:
        params["goods_status"] = args.status  # 1=在售, 0=下架

    result = call_api(args.shop_id, "pdd.goods.list.get", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_detail(args):
    """获取商品详情"""
    params = {"goods_id": str(args.goods_id)}
    result = call_api(args.shop_id, "pdd.goods.detail.get", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_update(args):
    """修改商品信息"""
    params = {"goods_id": str(args.goods_id)}

    if args.title:
        params["goods_name"] = args.title
    if args.description:
        params["goods_desc"] = args.description
    if args.short_description:
        params["goods_short_description"] = args.short_description

    result = call_api(args.shop_id, "pdd.goods.commit", params)

    if "error_response" not in result:
        print(f"商品 {args.goods_id} 修改成功！")
        if args.title:
            print(f"  新标题: {args.title}")
        if args.description:
            print(f"  详情页已更新（{len(args.description)}字）")
    else:
        print(f"修改失败: {result['error_response'].get('error_msg', '未知错误')}")


def cmd_stock(args):
    """同步库存"""
    params = {
        "goods_id": str(args.goods_id),
        "sku_id": str(args.sku_id),
        "quantity": str(args.quantity),
    }
    result = call_api(args.shop_id, "pdd.goods.quantity.update", params)

    if "error_response" not in result:
        print(f"商品 {args.goods_id} SKU {args.sku_id} 库存更新为 {args.quantity}")
    else:
        print(f"库存更新失败: {result['error_response'].get('error_msg', '未知错误')}")


def cmd_listing(args):
    """商品上下架"""
    if args.action == "on":
        method = "pdd.goods.sale.status.set"
        params = {
            "goods_id": str(args.goods_id),
            "is_onsale": "1",  # 1=上架, 0=下架
        }
    elif args.action == "off":
        method = "pdd.goods.sale.status.set"
        params = {
            "goods_id": str(args.goods_id),
            "is_onsale": "0",
        }
    else:
        print(f"未知操作: {args.action}，请使用 on 或 off")
        return

    result = call_api(args.shop_id, method, params)

    action_cn = "上架" if args.action == "on" else "下架"
    if "error_response" not in result:
        print(f"商品 {args.goods_id} 已{action_cn}")
    else:
        print(f"{action_cn}失败: {result['error_response'].get('error_msg', '未知错误')}")


def cmd_search_hot(args):
    """搜索平台热搜商品（用于竞品分析）"""
    params = {"keyword": args.keyword}
    result = call_api(args.shop_id, "pdd.goods.search", params)

    if "goods_list" in result:
        goods = result["goods_list"]
        print(f"搜索 [{args.keyword}] 找到 {len(goods)} 个结果：")
        print(f"{'排名':<5} {'商品名':<40} {'价格':<10} {'销量'}")
        print("-" * 75)
        for i, g in enumerate(goods[:args.top], 1):
            name = g.get("goods_name", "")[:38]
            price = f"¥{g.get('min_group_price', 0)/100:.2f}"
            sales = g.get("sales_tip", "-")
            print(f"{i:<5} {name:<40} {price:<10} {sales}")
    else:
        print("搜索结果为空或API调用异常")


def cmd_low_traffic(args):
    """检测低流量商品"""
    params = {"page": "1", "page_size": "50"}
    result = call_api(args.shop_id, "pdd.goods.list.get", params)

    if "goods_list" not in result:
        print("无法获取商品列表")
        return

    goods_list = result["goods_list"]
    low_traffic = []

    print(f"正在检测 {len(goods_list)} 个商品的流量...")

    for g in goods_list:
        detail_result = call_api(args.shop_id, "pdd.goods.detail.get",
                                 {"goods_id": str(g["goods_id"])})
        if "goods_detail" in detail_result:
            detail = detail_result["goods_detail"]
            pv_7d = detail.get("pv_7d", 0) or 0
            if pv_7d < args.threshold:
                low_traffic.append({
                    "goods_id": g["goods_id"],
                    "goods_name": g.get("goods_name", ""),
                    "pv_7d": pv_7d,
                })

    # 按流量从低到高排序
    low_traffic.sort(key=lambda x: x["pv_7d"])

    print(f"\n低流量商品（7日PV < {args.threshold}）：共 {len(low_traffic)} 个")
    print(f"{'商品ID':<15} {'商品名称':<40} {'7日PV'}")
    print("-" * 70)
    for item in low_traffic:
        print(f"{item['goods_id']:<15} {item['goods_name'][:38]:<40} {item['pv_7d']}")

    return low_traffic


def cmd_upload(args):
    """上传新商品"""
    # 构建商品信息
    goods_info = {
        "goods_name": args.title,
        "goods_desc": args.description or "",
        "cat_id": args.cat_id,
        "country_id": args.country_id or "1",
        "market_price": str(int(float(args.market_price) * 100)),
        "is_pre_sale": args.pre_sale or "0",
        "pre_sale_time": args.pre_sale_time or "",
        "shipment_limit_second": args.shipment_limit or "86400",  # 默认24h发货
    }

    # SKU信息
    if args.sku_info:
        goods_info["sku_info"] = args.sku_info

    result = call_api(args.shop_id, "pdd.goods.add", goods_info)

    if "goods_id" in result:
        print(f"商品上传成功！商品ID: {result['goods_id']}")
    else:
        print(f"上传失败: {result.get('error_response', {}).get('error_msg', '未知错误')}")


def main():
    parser = argparse.ArgumentParser(description="拼多多商品管理")
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="商品列表")
    p_list.add_argument("--shop-id", required=True)
    p_list.add_argument("--page", type=int, default=1)
    p_list.add_argument("--page-size", type=int, default=20)
    p_list.add_argument("--status", help="状态: 1=在售, 0=下架")

    # detail
    p_detail = sub.add_parser("detail", help="商品详情")
    p_detail.add_argument("--shop-id", required=True)
    p_detail.add_argument("--goods-id", required=True)

    # update
    p_update = sub.add_parser("update", help="修改商品")
    p_update.add_argument("--shop-id", required=True)
    p_update.add_argument("--goods-id", required=True)
    p_update.add_argument("--title")
    p_update.add_argument("--description")
    p_update.add_argument("--short-description")

    # stock
    p_stock = sub.add_parser("stock", help="更新库存")
    p_stock.add_argument("--shop-id", required=True)
    p_stock.add_argument("--goods-id", required=True)
    p_stock.add_argument("--sku-id", required=True)
    p_stock.add_argument("--quantity", type=int, required=True)

    # listing (上架/下架)
    p_listing = sub.add_parser("listing", help="商品上下架")
    p_listing.add_argument("--shop-id", required=True)
    p_listing.add_argument("--goods-id", required=True)
    p_listing.add_argument("--action", required=True, choices=["on", "off"])

    # search-hot
    p_search = sub.add_parser("search-hot", help="搜索热搜商品（竞品分析）")
    p_search.add_argument("--shop-id", required=True)
    p_search.add_argument("--keyword", required=True)
    p_search.add_argument("--top", type=int, default=20)

    # low-traffic
    p_low = sub.add_parser("low-traffic", help="低流量商品检测")
    p_low.add_argument("--shop-id", required=True)
    p_low.add_argument("--days", type=int, default=7)
    p_low.add_argument("--threshold", type=int, default=100, help="7日PV阈值")

    # upload
    p_upload = sub.add_parser("upload", help="上传新商品")
    p_upload.add_argument("--shop-id", required=True)
    p_upload.add_argument("--title", required=True)
    p_upload.add_argument("--cat-id", required=True)
    p_upload.add_argument("--market-price", required=True)
    p_upload.add_argument("--description")
    p_upload.add_argument("--country-id", default="1")
    p_upload.add_argument("--pre-sale", default="0")
    p_upload.add_argument("--pre-sale-time")
    p_upload.add_argument("--shipment-limit", default="86400")
    p_upload.add_argument("--sku-info")

    args = parser.parse_args()

    commands = {
        "list": cmd_list, "detail": cmd_detail, "update": cmd_update,
        "stock": cmd_stock, "listing": cmd_listing, "search-hot": cmd_search_hot,
        "low-traffic": cmd_low_traffic, "upload": cmd_upload,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
