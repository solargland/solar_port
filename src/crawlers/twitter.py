import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from .base import BaseCrawler, NewsItem

class TwitterTrendsCrawler(BaseCrawler):
    name = "TwitterTrendsCrawler"

    COUNTRY_SLUGS = {
        "美国": "united-states",
        "英国": "united-kingdom",
        "日本": "japan",
        "德国": "germany",
        "法国": "france",
        "全球": ""
    }

    def __init__(self, country: str = "美国", timeout: int = 15):
        super().__init__(timeout=timeout)
        self.country = country
        self.platform = "X (Twitter) 趋势"
        self.slug = self.COUNTRY_SLUGS.get(country, "united-states")

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = f"https://trends24.in/{self.slug}/" if self.slug else "https://trends24.in/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ja;q=0.8,zh-CN;q=0.7",
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()
        res.encoding = "utf-8"

        soup = BeautifulSoup(res.text, "html.parser")
        # trends24 页面包含每小时的趋势列表，首个列表即为当前最新实时趋势
        first_list = soup.select_one("ol.trend-card__list, .trend-card__list")
        if not first_list:
            return []

        trend_elements = first_list.select("li")
        results = []
        for elem in trend_elements:
            a_tag = elem.select_one("a")
            if not a_tag:
                continue
            trend_text = a_tag.text.strip()
            if not trend_text:
                continue

            # 抓取推文数量（如果有）
            count_span = elem.select_one(".tweet-count")
            extra_info = count_span.text.strip() if count_span else ""

            # 统一转为 Twitter/X 官方搜索链接
            search_url = f"https://x.com/search?q={urllib.parse.quote(trend_text)}"

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=trend_text,
                url=search_url,
                extra=f"推文讨论量: {extra_info}" if extra_info else "实时热门话题",
                summary=f"X (Twitter) {self.country} 地区实时热门话题榜第 {len(results)+1} 位"
            ))
            if len(results) >= limit:
                break

        return results
