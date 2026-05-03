#!/usr/bin/env python3
"""
抖音小店开放平台 — 认证与Token管理
支持多店铺、Token自动刷新、授权码模式
"""

import os
import json
import time
import hashlib
import urllib.parse
import urllib.request
import argparse
import sys
from datetime import datetime, timedelta

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", ".douyin_config")
TOKEN_FILE = os.path.join(CONFIG_DIR, "shops.json")
API_GATEWAY = "https://open-api.fuxi.douyin.com"
TOKEN_URL = "https://open-api.fuxi.douyin.com/oauth2/access_token"
AUTH_URL = "https://open.douyin.com/platform/oauth/connect"

SCOPES = "product_base,order_base,product_comment,im,refund,shop_data,kol_base"


def ensure_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)


def load_shops():
    ensure_config()
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_shops(shops):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)


def api_call(shop_id, path, params=None, method="POST"):
    """通用抖音小店API调用"""
    shops = load_shops()
    if shop_id not in shops:
        return {"error": f"店铺 {shop_id} 未配置"}

    shop = shops[shop_id]
    token = shop.get("access_token", "")

    url = API_GATEWAY + path
    headers = {
        "Content-Type": "application/json",
        "access-token": token,
    }

    try:
        data = json.dumps(params or {}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            # 检查Token过期
            if result.get("err_no") in [10002, 10003, 10004]:
                _refresh_token(shop_id)
                # 重试一次
                headers["access-token"] = load_shops()[shop_id]["access_token"]
                req2 = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req2, timeout=15) as resp2:
                    return json.loads(resp2.read().decode("utf-8"))
            return result
    except Exception as e:
        return {"error": str(e)}


def cmd_init(args):
    """初始化店铺认证"""
    shops = load_shops()
    shops[args.shop_id] = {
        "shop_name": args.shop_name,
        "app_key": args.app_key,
        "app_secret": args.app_secret,
        "created_at": datetime.now().isoformat(),
    }
    save_shops(shops)

    redirect_param = urllib.parse.quote("https://open.douyin.com")
    auth_url = (
        f"{AUTH_URL}?"
        f"client_key={args.app_key}"
        f"&response_type=code"
        f"&scope={SCOPES}"
        f"&redirect_uri={redirect_param}"
        f"&state={args.shop_id}"
    )
    print(json.dumps({
        "status": "ok",
        "shop_id": args.shop_id,
        "shop_name": args.shop_name,
        "auth_url": auth_url,
        "message": "请复制auth_url在抖音中打开，选择店铺后完成授权获取code"
    }, ensure_ascii=False))


def cmd_code(args):
    """用授权码换取Token"""
    shops = load_shops()
    if args.shop_id not in shops:
        print(json.dumps({"error": f"店铺 {args.shop_id} 未初始化"}))
        return
    shop = shops[args.shop_id]

    params = {
        "grant_type": "authorization_code",
        "code": args.code,
        "client_id": shop["app_key"],
        "client_secret": shop["app_secret"],
    }
    try:
        data = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(TOKEN_URL, data=data)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            data_part = result.get("data", result)
            if data_part.get("access_token"):
                shop["access_token"] = data_part["access_token"]
                shop["refresh_token"] = data_part.get("refresh_token", "")
                shop["shop_id"] = data_part.get("shop_id", args.shop_id)
                shop["expires_at"] = (
                    datetime.now() + timedelta(seconds=data_part.get("expires_in", 2592000))
                ).isoformat()
                shop["token_updated_at"] = datetime.now().isoformat()
                save_shops(shops)
                print(json.dumps({"status": "ok", "shop_id": args.shop_id, "message": "Token获取成功"}))
            else:
                print(json.dumps({"error": "Token获取失败", "detail": result}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


def cmd_refresh(args):
    """刷新Token"""
    shops = load_shops()
    if args.shop_id == "all":
        for sid in shops:
            _refresh_token(sid)
    else:
        _refresh_token(args.shop_id)


def _refresh_token(shop_id):
    shops = load_shops()
    if shop_id not in shops:
        return
    shop = shops[shop_id]
    if not shop.get("refresh_token"):
        return

    params = {
        "grant_type": "refresh_token",
        "client_id": shop["app_key"],
        "client_secret": shop["app_secret"],
        "refresh_token": shop["refresh_token"],
    }
    try:
        data = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(TOKEN_URL, data=data)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            data_part = result.get("data", result)
            if data_part.get("access_token"):
                shop["access_token"] = data_part["access_token"]
                shop["refresh_token"] = data_part.get("refresh_token", shop["refresh_token"])
                shop["expires_at"] = (
                    datetime.now() + timedelta(seconds=data_part.get("expires_in", 2592000))
                ).isoformat()
                shop["token_updated_at"] = datetime.now().isoformat()
                save_shops(shops)
    except:
        pass


def cmd_list(_args):
    shops = load_shops()
    shop_list = []
    for sid, shop in shops.items():
        has_token = bool(shop.get("access_token"))
        expires = shop.get("expires_at", "")
        expired = False
        if expires:
            try:
                expired = datetime.fromisoformat(expires) < datetime.now()
            except:
                pass
        shop_list.append({
            "shop_id": sid,
            "shop_name": shop.get("shop_name", ""),
            "has_token": has_token,
            "expired": expired,
            "expires_at": expires[:10] if expires else "",
        })
    print(json.dumps({"shops": shop_list, "total": len(shop_list)}, ensure_ascii=False))


def cmd_remove(args):
    shops = load_shops()
    if args.shop_id in shops:
        del shops[args.shop_id]
        save_shops(shops)
        print(json.dumps({"status": "ok", "shop_id": args.shop_id, "message": "已删除"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抖音小店 多店铺认证管理")
    sub = parser.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init")
    sp.add_argument("--shop-id", required=True)
    sp.add_argument("--shop-name", required=True)
    sp.add_argument("--app-key", required=True)
    sp.add_argument("--app-secret", required=True)

    sp = sub.add_parser("code")
    sp.add_argument("--shop-id", required=True)
    sp.add_argument("--code", required=True)

    sp = sub.add_parser("refresh")
    sp.add_argument("--shop-id", default="all")

    sub.add_parser("list")
    sp = sub.add_parser("remove")
    sp.add_argument("--shop-id", required=True)

    args = parser.parse_args()
    {"init": cmd_init, "code": cmd_code, "refresh": cmd_refresh, "list": cmd_list, "remove": cmd_remove}[args.command](args)
