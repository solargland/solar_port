import os
import sys
import argparse
import logging
from src.core.aggregator import NewsAggregator
from src.reporters import MarkdownReporter, HTMLReporter
from src.notifier import EmailNotifier

# 确保 Windows 下控制台能正常输出 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("GlobalNewsCrawler")

def run_pipeline(
    limit: int = 5,
    selected_countries: list = None,
    send_email: bool = False,
    output_dir: str = "daily_reports",
    edition: str = "auto"
):
    aggregator = NewsAggregator()
    md_reporter = MarkdownReporter(output_dir=output_dir)
    html_reporter = HTMLReporter(output_dir=output_dir)
    notifier = EmailNotifier()

    # 执行并发爬取
    data = aggregator.crawl_all(limit=limit, selected_countries=selected_countries, edition=edition)
    cur_edition = data.get("edition", "热点")

    print("=" * 65)
    print(f"🌐 全球主流社交媒体每日热点爬虫【{cur_edition}】")
    print("=" * 65)

    # 生成 Markdown 报告
    md_path = md_reporter.save(data)
    print(f"\n[+] Markdown 日报已生成: {md_path}")

    # 生成 HTML 可视化看板
    html_path = html_reporter.save(data)
    print(f"[+] HTML 交互看板已生成: {html_path}")

    # 发送邮件（如果指定）
    if send_email:
        print(f"[*] 正在准备发送【{cur_edition}】邮件...")
        subject = f"【全球社交{cur_edition}】{data.get('date')} 主流国家前五热点聚合"
        html_content = html_reporter.render(data)
        text_content = md_reporter.render(data)
        success = notifier.send_report(subject, html_content=html_content, text_content=text_content)
        if success:
            print(f"[+] 【{cur_edition}】邮件推送成功！")
        else:
            print("[-] 邮件未发送或发送失败，请检查配置。")

    print("\n" + "=" * 65)
    print(f"🎉 任务圆满完成！共汇总 {data.get('total_items')} 条最新社交舆情。")
    print(f"💡 双击打开 HTML 看板查看: {html_path}")
    print("=" * 65)
    return md_path, html_path

def main():
    parser = argparse.ArgumentParser(description="全球主流社交媒体每日热点前五爬虫系统")
    parser.add_argument("--limit", type=int, default=5, help="每个平台抓取条目数 (默认 5)")
    parser.add_argument("--country", type=str, default="", help="指定抓取国家，逗号分隔，如: 中国,美国,日本")
    parser.add_argument("--edition", type=str, default="auto", choices=["auto", "早报", "晚报"], help="报告期号 (auto / 早报 / 晚报)")
    parser.add_argument("--send-email", action="store_true", help="抓取完成后自动发送邮件汇报")
    parser.add_argument("--output-dir", type=str, default="daily_reports", help="报告输出目录")
    parser.add_argument("--dry-run", action="store_true", help="测试运行各源可用性")

    args = parser.parse_args()

    selected = [c.strip() for c in args.country.split(",") if c.strip()] if args.country else None

    if args.dry_run:
        print("[*] 正在进行 Dry Run 连通性测试 (每源取 1 条)...")
        run_pipeline(limit=1, selected_countries=selected, send_email=False, output_dir="daily_reports", edition=args.edition)
    else:
        run_pipeline(
            limit=args.limit,
            selected_countries=selected,
            send_email=args.send_email,
            output_dir=args.output_dir,
            edition=args.edition
        )

if __name__ == "__main__":
    main()
