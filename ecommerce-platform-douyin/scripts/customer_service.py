#!/usr/bin/env python3
"""抖音小店 — 客服消息（飞鸽消息接收/发送/撤回）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import api_call


def cmd_receive(args):
    r = api_call(args.shop_id, "/im/getMsgList", {
        "user_id": args.user_id or None,
        "page": args.page or 1,
        "size": args.size or 20,
        "start_time": args.start or None,
        "end_time": args.end or None,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_send(args):
    msg_type = args.msg_type or "text"
    payload = {
        "user_id": args.user_id,
        "msg_type": msg_type,
    }
    if msg_type == "text":
        payload["text"] = args.content
    elif msg_type == "image":
        payload["image"] = {"src": args.content}
    elif msg_type == "card":
        payload["card"] = json.loads(args.content) if args.content else {}

    r = api_call(args.shop_id, "/im/sendMsg", payload)
    print(json.dumps(r, ensure_ascii=False))


def cmd_recall(args):
    r = api_call(args.shop_id, "/im/recallMsg", {"msg_id": args.msg_id})
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="抖音飞鸽客服消息")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("receive"); s.add_argument("--shop-id", required=True)
    s.add_argument("--user-id"); s.add_argument("--page", type=int); s.add_argument("--size", type=int); s.add_argument("--start"); s.add_argument("--end")
    s = sp.add_parser("send"); s.add_argument("--shop-id", required=True); s.add_argument("--user-id", required=True); s.add_argument("--content", required=True)
    s.add_argument("--msg-type", default="text")
    s = sp.add_parser("recall"); s.add_argument("--shop-id", required=True); s.add_argument("--msg-id", required=True)

    a = p.parse_args()
    {"receive": cmd_receive, "send": cmd_send, "recall": cmd_recall}[a.cmd](a)
