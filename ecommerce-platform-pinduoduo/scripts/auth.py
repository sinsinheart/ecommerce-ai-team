"""
拼多多多店铺认证与Token管理
支持多个拼多多店铺的统一认证和Token自动刷新

Usage:
    python auth.py init --shop-id <id> --shop-name <name> --client-id <id> --client-secret <secret>
    python auth.py refresh --shop-id <id>
    python auth.py list
    python auth.py remove --shop-id <id>
    python auth.py get-token --shop-id <id>
"""

import json
import os
import sys
import time
import hashlib
import argparse
import urllib.request
import urllib.parse
from pathlib import Path

# 配置目录
CONFIG_DIR = Path(os.environ.get("EASYCLAW_WORKSPACE", str(Path.home() / ".easyclaw" / "workspace"))) / ".pdd"
TOKEN_FILE = CONFIG_DIR / "tokens.json"
SHOP_FILE = CONFIG_DIR / "shops.json"

# PDD API 端点
PDD_AUTH_URL = "https://open-api.pinduoduo.com/oauth/token"
PDD_API_BASE = "https://open-api.pinduoduo.com"


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(filepath, data):
    ensure_config_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_sign(params, client_secret):
    """生成拼多多API签名"""
    sorted_keys = sorted(params.keys())
    sign_str = client_secret
    for key in sorted_keys:
        sign_str += key + str(params[key])
    sign_str += client_secret
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()


def call_api(shop_id, method, params, access_token=None):
    """调用拼多多开放平台API"""
    shops = load_json(SHOP_FILE)
    tokens = load_json(TOKEN_FILE)

    if shop_id not in shops:
        return {"error": f"店铺 {shop_id} 未配置"}

    shop = shops[shop_id]
    token_data = tokens.get(shop_id, {})

    if access_token is None:
        access_token = token_data.get("access_token")

    if not access_token:
        return {"error": "未获取到access_token，请先执行 auth init"}

    # 构建公共参数
    public_params = {
        "type": method,
        "client_id": shop["client_id"],
        "access_token": access_token,
        "timestamp": str(int(time.time())),
        "data_type": "JSON",
    }
    public_params.update(params)
    public_params["sign"] = generate_sign(public_params, shop["client_secret"])

    try:
        data = urllib.parse.urlencode(public_params).encode("utf-8")
        req = urllib.request.Request(PDD_API_BASE, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def cmd_init(args):
    """初始化店铺认证"""
    shops = load_json(SHOP_FILE)

    shop_config = {
        "shop_id": args.shop_id,
        "shop_name": args.shop_name,
        "client_id": args.client_id,
        "client_secret": args.client_secret,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    shops[args.shop_id] = shop_config
    save_json(SHOP_FILE, shops)

    # 获取初始token
    print(f"正在为店铺 [{args.shop_name}] 获取access_token...")
    print(f"请访问以下URL获取授权码：")
    print(f"https://mms.pinduoduo.com/open.html?client_id={args.client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code")
    print(f"授权后，将授权码粘贴到下方（或在命令行执行 auth code --shop-id {args.shop_id} --code <授权码>）：")

    print(f"\n店铺 [{args.shop_name}] 初始化完成，待输入授权码获取Token")


def cmd_code(args):
    """使用授权码获取Token"""
    shops = load_json(SHOP_FILE)
    if args.shop_id not in shops:
        print(f"错误: 店铺 {args.shop_id} 未初始化")
        return

    shop = shops[args.shop_id]

    params = {
        "client_id": shop["client_id"],
        "client_secret": shop["client_secret"],
        "grant_type": "authorization_code",
        "code": args.code,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    }

    try:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(PDD_AUTH_URL, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if "access_token" in result:
            tokens = load_json(TOKEN_FILE)
            tokens[args.shop_id] = {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", ""),
                "expires_in": result.get("expires_in", 86400),
                "owner_id": result.get("owner_id", ""),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_json(TOKEN_FILE, tokens)
            print(f"店铺 [{shop['shop_name']}] Token获取成功！")
            print(f"  access_token: {result['access_token'][:20]}...")
            print(f"  有效期: {result.get('expires_in', 86400)}秒")
        else:
            print(f"Token获取失败: {result}")
    except Exception as e:
        print(f"请求失败: {e}")


def cmd_refresh(args):
    """刷新Token"""
    shops = load_json(SHOP_FILE)
    tokens = load_json(TOKEN_FILE)

    if args.shop_id not in shops or args.shop_id not in tokens:
        print(f"错误: 店铺 {args.shop_id} 未完成认证")
        return

    shop = shops[args.shop_id]
    token_data = tokens[args.shop_id]

    params = {
        "client_id": shop["client_id"],
        "client_secret": shop["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": token_data.get("refresh_token", ""),
    }

    try:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(PDD_AUTH_URL, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if "access_token" in result:
            tokens[args.shop_id].update({
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", token_data.get("refresh_token")),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            })
            save_json(TOKEN_FILE, tokens)
            print(f"店铺 [{shop['shop_name']}] Token刷新成功！")
        else:
            print(f"Token刷新失败: {result}")
    except Exception as e:
        print(f"请求失败: {e}")


def cmd_list(args):
    """列出所有已配置店铺"""
    shops = load_json(SHOP_FILE)
    tokens = load_json(TOKEN_FILE)

    if not shops:
        print("暂无已配置店铺")
        return

    print(f"{'Shop ID':<20} {'店铺名称':<20} {'Token状态':<10} {'更新时间'}")
    print("-" * 80)
    for sid, shop in shops.items():
        token_info = tokens.get(sid, {})
        status = "有效" if token_info.get("access_token") else "待授权"
        updated = token_info.get("updated_at", "-")
        print(f"{sid:<20} {shop['shop_name']:<20} {status:<10} {updated}")


def cmd_get_token(args):
    """获取指定店铺的access_token"""
    tokens = load_json(TOKEN_FILE)
    token_data = tokens.get(args.shop_id, {})
    token = token_data.get("access_token", "")

    if args.output == "json":
        print(json.dumps({
            "shop_id": args.shop_id,
            "access_token": token,
            "has_token": bool(token),
        }))
    else:
        print(token if token else "未获取到Token")


def cmd_remove(args):
    """移除店铺配置"""
    shops = load_json(SHOP_FILE)
    tokens = load_json(TOKEN_FILE)

    if args.shop_id in shops:
        del shops[args.shop_id]
        save_json(SHOP_FILE, shops)
        print(f"店铺 {args.shop_id} 配置已移除")

    if args.shop_id in tokens:
        del tokens[args.shop_id]
        save_json(TOKEN_FILE, tokens)
        print(f"店铺 {args.shop_id} Token已清除")


def main():
    parser = argparse.ArgumentParser(description="拼多多多店铺认证管理")
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="初始化店铺")
    p_init.add_argument("--shop-id", required=True)
    p_init.add_argument("--shop-name", required=True)
    p_init.add_argument("--client-id", required=True)
    p_init.add_argument("--client-secret", required=True)

    # code (authorization code)
    p_code = sub.add_parser("code", help="输入授权码获取Token")
    p_code.add_argument("--shop-id", required=True)
    p_code.add_argument("--code", required=True)

    # refresh
    p_refresh = sub.add_parser("refresh", help="刷新Token")
    p_refresh.add_argument("--shop-id", required=True)

    # list
    sub.add_parser("list", help="列出所有店铺")

    # get-token
    p_token = sub.add_parser("get-token", help="获取access_token")
    p_token.add_argument("--shop-id", required=True)
    p_token.add_argument("--output", choices=["text", "json"], default="text")

    # remove
    p_remove = sub.add_parser("remove", help="移除店铺")
    p_remove.add_argument("--shop-id", required=True)

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "code":
        cmd_code(args)
    elif args.command == "refresh":
        cmd_refresh(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "get-token":
        cmd_get_token(args)
    elif args.command == "remove":
        cmd_remove(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
