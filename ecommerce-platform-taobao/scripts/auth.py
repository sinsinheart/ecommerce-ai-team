#!/usr/bin/env python3
"""
淘宝/天猫开放平台 — 认证与Token管理
支持多店铺、Token自动刷新、凭证安全存储
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

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", ".taobao_config")
TOKEN_FILE = os.path.join(CONFIG_DIR, "shops.json")
API_GATEWAY = "https://eco.taobao.com/router/rest"
TOKEN_URL = "https://oauth.taobao.com/token"
AUTH_URL = "https://oauth.taobao.com/authorize"


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


def sign(params, app_secret):
    """淘宝API签名: MD5(app_secret + 排序后的参数)"""
    sorted_keys = sorted(params.keys())
    sign_str = app_secret
    for k in sorted_keys:
        sign_str += k + str(params[k])
    sign_str += app_secret
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()


def call_api(shop_id, method, extra_params):
    """通用淘宝API调用"""
    shops = load_shops()
    if shop_id not in shops:
        print(json.dumps({"error": f"店铺 {shop_id} 未配置"}))
        return None

    shop = shops[shop_id]
    token = shop.get("access_token", "")
    app_key = shop.get("app_key", "")
    app_secret = shop.get("app_secret", "")

    params = {
        "method": method,
        "app_key": app_key,
        "session": token,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "md5",
    }
    params.update(extra_params)
    params["sign"] = sign(params, app_secret)

    url = API_GATEWAY + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return None


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
    auth_redir = "urn:ietf:wg:oauth:2.0:oob" if not args.redirect else args.redirect
    redirect_param = urllib.parse.quote(auth_redir)
    auth_url = (
        f"https://oauth.taobao.com/authorize?"
        f"response_type=code&client_id={args.app_key}"
        f"&redirect_uri={redirect_param}&state={args.shop_id}"
    )
    print(json.dumps({
        "status": "ok",
        "shop_id": args.shop_id,
        "shop_name": args.shop_name,
        "auth_url": auth_url,
        "message": "请复制auth_url在浏览器中打开，完成授权后获取code"
    }, ensure_ascii=False))


def cmd_code(args):
    """用授权码换取Token"""
    shops = load_shops()
    if args.shop_id not in shops:
        print(json.dumps({"error": f"店铺 {args.shop_id} 未初始化"}))
        return
    shop = shops[args.shop_id]
    app_key = shop["app_key"]
    app_secret = shop["app_secret"]
    redirect_uri = shop.get("redirect_uri", "urn:ietf:wg:oauth:2.0:oob")

    params = {
        "grant_type": "authorization_code",
        "code": args.code,
        "client_id": app_key,
        "client_secret": app_secret,
        "redirect_uri": redirect_uri,
    }
    try:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(TOKEN_URL, data=data)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if "access_token" in result:
                shop["access_token"] = result["access_token"]
                shop["refresh_token"] = result.get("refresh_token", "")
                shop["expires_at"] = (datetime.now() + timedelta(seconds=result.get("expires_in", 2592000))).isoformat()
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
        print(json.dumps({"error": f"店铺 {shop_id} 未配置"}))
        return
    shop = shops[shop_id]
    if not shop.get("refresh_token"):
        print(json.dumps({"error": f"店铺 {shop_id} 无refresh_token，请重新授权"}))
        return

    params = {
        "grant_type": "refresh_token",
        "client_id": shop["app_key"],
        "client_secret": shop["app_secret"],
        "refresh_token": shop["refresh_token"],
    }
    try:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(TOKEN_URL, data=data)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if "access_token" in result:
                shop["access_token"] = result["access_token"]
                shop["refresh_token"] = result.get("refresh_token", shop["refresh_token"])
                shop["expires_at"] = (datetime.now() + timedelta(seconds=result.get("expires_in", 2592000))).isoformat()
                shop["token_updated_at"] = datetime.now().isoformat()
                save_shops(shops)
                print(json.dumps({"status": "ok", "shop_id": shop_id, "message": "Token刷新成功"}))
            else:
                print(json.dumps({"error": "刷新失败", "detail": result}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


def cmd_list(_args):
    """列出已配置的店铺"""
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
    else:
        print(json.dumps({"error": f"店铺 {args.shop_id} 不存在"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="淘宝/天猫 多店铺认证管理")
    sub = parser.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init")
    sp.add_argument("--shop-id", required=True)
    sp.add_argument("--shop-name", required=True)
    sp.add_argument("--app-key", required=True)
    sp.add_argument("--app-secret", required=True)
    sp.add_argument("--redirect", default="")

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
