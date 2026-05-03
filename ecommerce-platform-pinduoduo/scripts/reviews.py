"""
拼多多评价管理API
支持评价全量抓取、追评监控、问答区监控、差评筛选

Usage:
    python reviews.py fetch --shop-id <id> --goods-id <id> [--rating 1-3] [--days 7]
    python reviews.py fetch-all --shop-id <id> [--days 1] [--max-rating 3]
    python reviews.py detail --shop-id <id> --review-id <id>
    python reviews.py stats --shop-id <id> [--days 30]
    python reviews.py questions --shop-id <id> --goods-id <id>
    python reviews.py negative-keywords --shop-id <id> --goods-id <id> [--days 30]
"""

import json
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from auth import call_api, load_json, TOKEN_FILE, SHOP_FILE

# 差评归因关键词库（与 review-management skill 同步）
NEGATIVE_PATTERNS = {
    "物流延迟": ["慢", "还没到", "等了好久", "快递太慢", "物流差", "迟迟不", "几天了", "龟速", "没有物流", "查不到", "延误", "超时", "配送慢"],
    "商品质量": ["质量差", "坏了", "烂了", "次品", "劣质", "掉色", "缩水", "起球", "变形", "开线", "脱胶", "异味", "瑕疵", "粗糙", "假货"],
    "尺码偏差": ["太大", "太小", "偏大", "偏小", "穿不上", "紧了", "松了", "不合身", "码数不准", "尺码不对", "版型不对", "偏瘦", "偏肥"],
    "色差问题": ["色差", "颜色不一样", "图片好看", "实物颜色", "暗了", "亮了", "不是这个颜色", "有色差", "颜色不准", "比图片深", "比图片浅"],
    "客服态度": ["客服差", "不理人", "回复慢", "态度差", "不解决", "敷衍", "踢皮球", "机器人", "半天不回", "没人管", "态度恶劣"],
    "发货速度": ["不发货", "虚假发货", "几天了没发", "发货慢", "迟迟不发", "没货也不说", "拍了一直不发", "超时未发", "承诺没做到"],
    "包装破损": ["包装差", "破了", "碎了", "烂了", "漏了", "磕碰", "挤压", "没有保护", "包装简陋", "就一个袋子", "没有泡沫", "摔坏了"],
    "实物不符": ["不一样", "不是同一款", "假的", "山寨", "挂羊头", "图文不符", "描述不符", "和图片不一样", "没想到", "上当", "欺骗"],
}


def classify_review(review_text):
    """AI归因分析（基于关键词匹配）"""
    if not review_text:
        return "未分类"

    scores = {}
    for category, keywords in NEGATIVE_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in review_text)
        if score > 0:
            scores[category] = score

    if not scores:
        return "其他"

    # 返回得分最高的分类
    return max(scores, key=scores.get)


def cmd_fetch(args):
    """抓取指定商品评价"""
    params = {"goods_id": str(args.goods_id), "page": "1", "page_size": "50"}

    if args.rating:
        params["rating"] = args.rating  # 1=差评, 2=中评, 3=好评

    result = call_api(args.shop_id, "pdd.goods.comments.get", params)

    if "comments_list" in result:
        comments = result["comments_list"]
        filtered = []

        # 时间过滤
        cutoff = datetime.now() - timedelta(days=args.days) if args.days else None

        for c in comments:
            comment_time = c.get("comment_time", "")
            if cutoff and comment_time:
                try:
                    ct = datetime.fromisoformat(comment_time)
                    if ct < cutoff:
                        continue
                except:
                    pass
            filtered.append(c)

        print(f"找到 {len(filtered)} 条评价：")
        for i, c in enumerate(filtered, 1):
            rating_stars = "★" * c.get("rating", 0) + "☆" * (5 - c.get("rating", 0))
            category = classify_review(c.get("comment", ""))
            print(f"\n--- 评价 {i} ---")
            print(f"  评分: {rating_stars}  |  分类: {category}")
            print(f"  用户: {c.get('user_name', '匿名')}")
            print(f"  内容: {c.get('comment', '(无内容)')[:100]}")
            print(f"  时间: {c.get('comment_time', '未知')}")
            if c.get("append_comment"):
                print(f"  追评: {c['append_comment'][:80]}  ⚠️")

        # 输出归因统计
        categories = {}
        for c in filtered:
            cat = classify_review(c.get("comment", ""))
            categories[cat] = categories.get(cat, 0) + 1

        if categories:
            print(f"\n=== 归因统计 ===")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                pct = count / len(filtered) * 100
                bar = "█" * int(pct / 5)
                print(f"  {cat:<8} {count:>3}条 ({pct:5.1f}%) {bar}")
    else:
        print("未获取到评价数据")


def cmd_fetch_all(args):
    """全店铺差评抓取"""
    # 先获取全店商品列表
    list_result = call_api(args.shop_id, "pdd.goods.list.get",
                           {"page": "1", "page_size": "100"})

    if "goods_list" not in list_result:
        print("无法获取商品列表")
        return

    goods_list = list_result["goods_list"]
    all_negative = []

    print(f"正在扫描 {len(goods_list)} 个商品的差评...")

    for g in goods_list:
        result = call_api(args.shop_id, "pdd.goods.comments.get",
                          {"goods_id": str(g["goods_id"]), "rating": "1-3", "page_size": "20"})

        if "comments_list" in result:
            cutoff = datetime.now() - timedelta(days=args.days)
            for c in result["comments_list"]:
                comment_time = c.get("comment_time", "")
                if cutoff and comment_time:
                    try:
                        ct = datetime.fromisoformat(comment_time)
                        if ct < cutoff:
                            continue
                    except:
                        pass

                category = classify_review(c.get("comment", ""))
                all_negative.append({
                    "goods_id": g["goods_id"],
                    "goods_name": g.get("goods_name", ""),
                    "rating": c.get("rating", 0),
                    "comment": c.get("comment", ""),
                    "user": c.get("user_name", "匿名"),
                    "time": c.get("comment_time", ""),
                    "category": category,
                })

    # 按评分从低到高排序
    all_negative.sort(key=lambda x: x["rating"])

    print(f"\n=== 全店铺差评汇总（{args.days}天内）===")
    print(f"共发现 {len(all_negative)} 条差评/中评\n")

    # 按归因分类统计
    cat_count = {}
    goods_count = {}
    for item in all_negative:
        cat_count[item["category"]] = cat_count.get(item["category"], 0) + 1
        gid = item["goods_id"]
        if gid not in goods_count:
            goods_count[gid] = {"name": item["goods_name"], "count": 0}
        goods_count[gid]["count"] += 1

    print("📊 差评归因分布：")
    for cat, count in sorted(cat_count.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(all_negative) * 100 if all_negative else 0
        bar = "█" * int(pct / 3)
        print(f"  {cat:<8} {count:>3}条 ({pct:5.1f}%) {bar}")

    print(f"\n⚠️ 问题TOP商品：")
    for gid, info in sorted(goods_count.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
        print(f"  {info['name'][:40]:<42} {info['count']}条差评")

    # 输出JSON（供其他模块消费）
    if args.output_json:
        output = {
            "total": len(all_negative),
            "period_days": args.days,
            "categories": cat_count,
            "top_goods": {gid: info for gid, info in
                         sorted(goods_count.items(), key=lambda x: x[1]["count"], reverse=True)[:5]},
            "reviews": all_negative,
            "generated_at": datetime.now().isoformat(),
        }
        print(f"\n{json.dumps(output, ensure_ascii=False)}")


def cmd_stats(args):
    """店铺评价统计"""
    result = call_api(args.shop_id, "pdd.goods.comments.stats.get", {"days": str(args.days)})

    if "stats" in result:
        stats = result["stats"]
        print(f"=== 店铺评价统计（{args.days}天）===")
        print(f"  好评率: {stats.get('good_rate', 0)}%")
        print(f"  中评率: {stats.get('mid_rate', 0)}%")
        print(f"  差评率: {stats.get('bad_rate', 0)}%")
        print(f"  总评价: {stats.get('total', 0)}条")
        print(f"  带图评价: {stats.get('with_image', 0)}条")
        print(f"  追评数: {stats.get('append_count', 0)}条")

        bad_rate = float(stats.get("bad_rate", 0))
        if bad_rate > 5:
            print(f"\n🔴 差评率 {bad_rate}% 超过5%警戒线！")
        elif bad_rate > 3:
            print(f"\n🟡 差评率 {bad_rate}% 需要关注")
    else:
        print("无法获取评价统计")


def cmd_questions(args):
    """问答区监控"""
    result = call_api(args.shop_id, "pdd.goods.questions.get",
                      {"goods_id": str(args.goods_id)})

    if "questions" in result:
        questions = result["questions"]
        negative_q = [q for q in questions
                      if any(kw in q.get("content", "") for kw in
                             ["不建议", "不推荐", "别买", "差", "不好", "后悔"])]

        print(f"商品问答区共 {len(questions)} 个问题")
        if negative_q:
            print(f"⚠️ 其中 {len(negative_q)} 个含负面内容：")
            for q in negative_q:
                print(f"  Q: {q.get('content', '')[:80]}")
                for a in q.get("answers", [])[:2]:
                    print(f"  A: {a.get('content', '')[:80]}")
                print()


def cmd_negative_keywords(args):
    """提取差评高频关键词"""
    result = call_api(args.shop_id, "pdd.goods.comments.get",
                      {"goods_id": str(args.goods_id), "rating": "1-3", "page_size": "100"})

    if "comments_list" not in result:
        print("未获取到差评数据")
        return

    # 简易TF统计
    word_count = {}
    for c in result["comments_list"]:
        comment = c.get("comment", "")
        for cat, keywords in NEGATIVE_PATTERNS.items():
            for kw in keywords:
                if kw in comment:
                    word_count[kw] = word_count.get(kw, 0) + 1

    # 排序输出
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    print(f"差评高频负面关键词 TOP20：")
    for i, (word, count) in enumerate(sorted_words[:20], 1):
        bar = "█" * min(count, 20)
        print(f"  {i:>2}. {word:<10} {count:>3}次 {bar}")


def main():
    parser = argparse.ArgumentParser(description="拼多多评价管理")
    sub = parser.add_subparsers(dest="command")

    # fetch
    p_fetch = sub.add_parser("fetch", help="抓取指定商品评价")
    p_fetch.add_argument("--shop-id", required=True)
    p_fetch.add_argument("--goods-id", required=True)
    p_fetch.add_argument("--rating", help="评分筛选: 1-3")
    p_fetch.add_argument("--days", type=int, default=7)

    # fetch-all
    p_all = sub.add_parser("fetch-all", help="全店铺差评抓取")
    p_all.add_argument("--shop-id", required=True)
    p_all.add_argument("--days", type=int, default=1)
    p_all.add_argument("--max-rating", type=int, default=3)
    p_all.add_argument("--output-json", action="store_true", help="输出JSON格式")

    # stats
    p_stats = sub.add_parser("stats", help="店铺评价统计")
    p_stats.add_argument("--shop-id", required=True)
    p_stats.add_argument("--days", type=int, default=30)

    # questions
    p_q = sub.add_parser("questions", help="问答区监控")
    p_q.add_argument("--shop-id", required=True)
    p_q.add_argument("--goods-id", required=True)

    # negative-keywords
    p_kw = sub.add_parser("negative-keywords", help="差评高频关键词提取")
    p_kw.add_argument("--shop-id", required=True)
    p_kw.add_argument("--goods-id", required=True)

    args = parser.parse_args()

    commands = {
        "fetch": cmd_fetch, "fetch-all": cmd_fetch_all, "stats": cmd_stats,
        "questions": cmd_questions, "negative-keywords": cmd_negative_keywords,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
