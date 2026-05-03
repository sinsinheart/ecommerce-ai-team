"""
拼多多客服消息API
支持消息接收、自动回复、会话管理

Usage:
    python customer_service.py messages --shop-id <id> [--limit 50]
    python customer_service.py reply --shop-id <id> --user-id <id> --message "亲，您好~"
    python customer_service.py session --shop-id <id> --user-id <id>
    python customer_service.py response-rate --shop-id <id>
    python customer_service.py auto-reply --shop-id <id> --user-id <id> --query "物流到哪了"
"""

import json
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from auth import call_api

# FAQ知识库
FAQ_KNOWLEDGE = {
    "物流": [
        "物流到哪了", "什么时候发货", "几天能到", "快递单号", "查物流",
        "还没收到", "还在路上"
    ],
    "售后": [
        "退货", "退款", "换货", "质量有问题", "坏了", "不满意",
        "怎么退", "退款流程"
    ],
    "尺码": [
        "尺码", "码数", "大小", "偏大", "偏小", "什么码", "穿多大",
        "尺寸", "身高体重"
    ],
    "优惠": [
        "优惠券", "便宜点", "打折", "活动", "满减", "包邮",
        "有没有优惠", "能不能便宜"
    ],
    "商品": [
        "材质", "面料", "颜色", "有货吗", "什么时候补货", "怎么选",
        "作用", "怎么用"
    ],
}

FAQ_ANSWERS = {
    "物流": "亲，您的订单已发货，一般3-5天送达哦~您可以在订单详情中查看物流进度。如有延迟请见谅，我们会帮您跟进！",
    "售后": "亲，我们支持7天无理由退换货。您可以在订单中申请售后，我们会尽快为您处理。如有质量问题请联系我们优先解决~",
    "尺码": "亲，建议您参考详情页的尺码表选择哦~如果不确定的话可以告诉我您的身高体重，我帮您推荐合适的尺码！",
    "优惠": "亲，可以关注店铺首页查看当前优惠活动哦~新客还有专享优惠券可以领取！",
    "商品": "亲，商品详情页有详细介绍哦~您想看的具体是哪方面呢？材质、颜色还是使用方法？",
}

# 差评风险信号词
RISK_SIGNALS = [
    "差评", "投诉", "举报", "曝光", "退款", "不解决就",
    "太失望", "坑人", "骗人", "垃圾", "再也不买",
]


def classify_intent(query):
    """分类用户咨询意图"""
    if not query:
        return "其他"

    for category, keywords in FAQ_KNOWLEDGE.items():
        for kw in keywords:
            if kw in query:
                return category
    return "其他"


def detect_risk(query):
    """检测差评风险"""
    if not query:
        return False, ""

    for signal in RISK_SIGNALS:
        if signal in query:
            return True, signal
    return False, ""


def cmd_messages(args):
    """获取未读消息"""
    result = call_api(args.shop_id, "pdd.message.list.get",
                      {"page_size": str(args.limit)})

    if "message_list" in result:
        messages = result["message_list"]
        print(f"共 {len(messages)} 条未读消息：\n")
        for i, m in enumerate(messages, 1):
            content = m.get("content", "")
            intent = classify_intent(content)
            is_risk, risk_signal = detect_risk(content)

            risk_tag = " 🔴差评风险" if is_risk else ""
            print(f"{'---' if i > 1 else ''}消息 {i}{risk_tag}")
            print(f"  用户: {m.get('user_name', '匿名')}")
            print(f"  内容: {content[:100]}")
            print(f"  意图: {intent}")
            print(f"  时间: {m.get('time', '')}")

            if is_risk:
                print(f"  ⚠️ 检测到风险信号: [{risk_signal}] → 建议立即人工介入")
            if intent != "其他":
                reply_preview = FAQ_ANSWERS.get(intent, "")[:80]
                print(f"  💬 建议回复: {reply_preview}...")
    else:
        print("暂无未读消息")


def cmd_reply(args):
    """发送消息"""
    result = call_api(args.shop_id, "pdd.message.send", {
        "to_user_id": str(args.user_id),
        "content": args.message,
    })

    if "error_response" not in result:
        print(f"消息已发送给用户 {args.user_id}")
        print(f"  内容: {args.message}")
    else:
        print(f"发送失败: {result['error_response'].get('error_msg')}")


def cmd_session(args):
    """查看会话历史"""
    result = call_api(args.shop_id, "pdd.message.session.get", {
        "user_id": str(args.user_id),
        "page_size": "50",
    })

    if "messages" in result:
        msgs = result["messages"]
        print(f"=== 与用户 {args.user_id} 的会话记录 ===")
        for m in msgs:
            direction = "买家→" if m.get("from_buyer") else "商家→"
            print(f"  [{m.get('time', '')}] {direction} {m.get('content', '')[:80]}")
    else:
        print("未找到会话记录")


def cmd_response_rate(args):
    """查看回复率"""
    result = call_api(args.shop_id, "pdd.message.stats.get", {})

    if "stats" in result:
        s = result["stats"]
        print(f"=== 客服数据 ===")
        print(f"  3分钟回复率: {s.get('reply_rate_3min', 0)}%")
        print(f"  平均响应时间: {s.get('avg_response_time', 0)}秒")
        print(f"  今日接待量: {s.get('today_visitors', 0)}人")
        print(f"  今日消息量: {s.get('today_messages', 0)}条")

        rate = float(s.get("reply_rate_3min", 100))
        if rate < 80:
            print(f"\n🔴 3分钟回复率 {rate}% < 80%，严重影响店铺评分！")
        elif rate < 90:
            print(f"\n🟡 3分钟回复率 {rate}%，需提升响应速度")
    else:
        print("无法获取客服数据")


def cmd_auto_reply(args):
    """自动回复（FAQ匹配）"""
    intent = classify_intent(args.query)
    is_risk, risk_signal = detect_risk(args.query)

    if is_risk:
        # 风险消息：发送安抚话术 + 升级人工
        reply = f"亲，非常抱歉给您带来了不愉快的体验！您的问题我已经记录，会优先为您处理。请您稍等，马上为您转接专人处理~"
        print(f"⚠️ 检测到差评风险信号 [{risk_signal}]")
        print(f"  自动回复: {reply}")
        print(f"  同时建议: 升级人工客服跟进，主动联系买家安抚")
    elif intent in FAQ_ANSWERS:
        reply = FAQ_ANSWERS[intent]
        print(f"意图识别: {intent}")
        print(f"自动回复: {reply}")
    else:
        reply = "亲，收到您的消息啦~您的问题我已记录，会尽快回复您！如有紧急问题可拨打店铺电话。"
        print(f"意图识别: 其他（未匹配FAQ）")
        print(f"兜底回复: {reply}")

    # 实际发送（需要时取消注释）
    # call_api(args.shop_id, "pdd.message.send", {
    #     "to_user_id": str(args.user_id),
    #     "content": reply,
    # })


def main():
    parser = argparse.ArgumentParser(description="拼多多客服消息")
    sub = parser.add_subparsers(dest="command")

    # messages
    p_msg = sub.add_parser("messages", help="未读消息列表")
    p_msg.add_argument("--shop-id", required=True)
    p_msg.add_argument("--limit", type=int, default=50)

    # reply
    p_reply = sub.add_parser("reply", help="发送消息")
    p_reply.add_argument("--shop-id", required=True)
    p_reply.add_argument("--user-id", required=True)
    p_reply.add_argument("--message", required=True)

    # session
    p_sess = sub.add_parser("session", help="会话历史")
    p_sess.add_argument("--shop-id", required=True)
    p_sess.add_argument("--user-id", required=True)

    # response-rate
    sub.add_parser("response-rate", help="客服数据").add_argument("--shop-id", required=True)

    # auto-reply
    p_auto = sub.add_parser("auto-reply", help="自动回复（FAQ）")
    p_auto.add_argument("--shop-id", required=True)
    p_auto.add_argument("--user-id", required=True)
    p_auto.add_argument("--query", required=True)

    args = parser.parse_args()

    commands = {
        "messages": cmd_messages, "reply": cmd_reply, "session": cmd_session,
        "response-rate": cmd_response_rate, "auto-reply": cmd_auto_reply,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
