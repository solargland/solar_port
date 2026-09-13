import os
from typing import Dict, Any

COUNTRY_ICONS = {
    "中国": "🇨🇳",
    "俄罗斯": "🇷🇺",
    "美国": "🇺🇸",
    "英国": "🇬🇧",
    "日本": "🇯🇵",
    "德国": "🇩🇪",
    "法国": "🇫🇷",
    "全球科技": "🌐",
    "全球": "🌍"
}

PLATFORM_ICONS = {
    "微博热搜": "🔥",
    "百度热搜": "🔍",
    "哔哩哔哩热搜": "📺",
    "哔哩哔哩热门": "📺",
    "俄新社 (RIA Novosti)": "🇷🇺",
    "塔斯社 (TASS)": "📡",
    "Lenta.ru (俄罗斯门户热榜)": "🔥",
    "X (Twitter) 趋势": "🐦",
    "Yahoo! JAPAN 热点要闻": "🇯🇵",
    "Google 每日热搜": "🔎",
    "主流权威要闻": "📰",
    "Hacker News (科技与商业)": "💻",
}

class MarkdownReporter:
    """Markdown 格式日报渲染与存储器"""

    def __init__(self, output_dir: str = "daily_reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def render(self, data: Dict[str, Any]) -> str:
        date_str = data.get("date", "")
        timestamp = data.get("timestamp", "")
        edition = data.get("edition", "热点速递")
        total_items = data.get("total_items", 0)
        countries_data = data.get("countries", {})

        lines = []
        lines.append(f"# 🌍 全球主流社交媒体【{edition}】聚焦 Top 5 ({date_str})")
        lines.append("")
        lines.append(f"> 📅 **采集时间**: `{timestamp}` ({edition})  ")
        lines.append(f"> 📊 **数据规模**: 覆盖 `{len(countries_data)}` 个国家/区域，共归集 `{total_items}` 条最新前沿舆论动态。  ")
        lines.append("> 💡 **注**: 点击各条目可直接跳转至原平台查看详细推文、讨论或新闻源。")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 目录导航
        lines.append("## 📑 快速目录索引")
        for country in sorted(countries_data.keys()):
            icon = COUNTRY_ICONS.get(country, "🌐")
            anchor = f"{country}"
            lines.append(f"- [{icon} {country}](#{anchor})")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 各国数据展示
        for country, platforms in sorted(countries_data.items()):
            c_icon = COUNTRY_ICONS.get(country, "🌐")
            lines.append(f"<h2 id=\"{country}\">{c_icon} {country} 社交与舆论热点</h2>")
            lines.append("")

            has_platform = False
            for platform, items in platforms.items():
                if not items:
                    continue
                has_platform = True
                p_icon = PLATFORM_ICONS.get(platform, "📌")
                lines.append(f"### {p_icon} {platform} Top {len(items)}")
                lines.append("")

                for it in items:
                    extra_str = f" `[{it.extra}]`" if it.extra else ""
                    lines.append(f"**{it.rank}.** [{it.title}]({it.url}){extra_str}")
                    if it.summary:
                        lines.append(f"   > *{it.summary}*")
                    lines.append("")

            if not has_platform:
                lines.append("*（该国家/地区当前暂无可用舆情数据）*")
                lines.append("")

            lines.append("---")
            lines.append("")

        lines.append("*(本报告由 Global Daily Social News Crawler 自动生成)*")
        return "\n".join(lines)

    def save(self, data: Dict[str, Any]) -> str:
        content = self.render(data)
        date_str = data.get("date", "latest")
        edition = data.get("edition", "热点")
        filepath = os.path.join(self.output_dir, f"{date_str}_{edition}_global_social_news.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.abspath(filepath)
