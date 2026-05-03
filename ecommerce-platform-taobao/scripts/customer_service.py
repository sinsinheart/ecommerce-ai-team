#!/usr/bin/env python3
"""淘宝/天猫 — 客服消息（旺旺消息接收/发送/会话管理）"""

import json, argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import call_api


def cmd_receive(args):
    """获取IM消息列表"""
    r = call_api(args.shop_id, "taobao.openim.messages.get", {
        "user_nick": args.user_nick or "",
        "start_time": args.start or "",
        "end_time": args.end or "",
        "page_no": args.page or 1,
        "page_size": args.size or 20,
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_send(args):
    """发送消息"""
    r = call_api(args.shop_id, "taobao.openim.messages.send", {
        "user_nick": args.user_nick,
        "msg_content": args.content,
        "msg_type": args.msg_type or "text",
    })
    print(json.dumps(r, ensure_ascii=False))


def cmd_auto_reply(args):
    """基于规则的自动回复（离线批量）"""
    rules = json.loads(args.rules) if args.rules else {}
    r = call_api(args.shop_id, "taobao.openim.custmsg.push", {
        "user_nick": args.user_nick,
        "msg_content": args.content,
    })
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="淘宝旺旺客服消息")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("receive"); s.add_argument("--shop-id", required=True)
    s.add_argument("--user-nick"); s.add_argument("--start"); s.add_argument("--end"); s.add_argument("--page", type=int); s.add_argument("--size", type=int)
    s = sp.add_parser("send"); s.add_argument("--shop-id", required=True); s.add_argument("--user-nick", required=True); s.add_argument("--content", required=True)
    s.add_argument("--msg-type", default="text")
    s = sp.add_parser("auto-reply"); s.add_argument("--shop-id", required=True); s.add_argument("--user-nick", required=True); s.add_argument("--content", required=True)
    s.add_argument("--rules")

    a = p.parse_args()
    {"receive": cmd_receive, "send": cmd_send, "auto-reply": cmd_auto_reply}[a.cmd](a)
