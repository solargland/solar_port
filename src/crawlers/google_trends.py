import html
import xml.etree.ElementTree as ET
from typing import List
from .base import BaseCrawler, NewsItem

class GoogleTrendsCrawler(BaseCrawler):
    name = "GoogleTrendsCrawler"

    COUNTRY_GEOS = {
        "美国": "US",
        "英国": "GB",
        "日本": "JP",
        "德国": "DE",
        "法国": "FR",
        "全球": "US"
    }

    def __init__(self, country: str = "美国", timeout: int = 15):
        super().__init__(timeout=timeout)
        self.country = country
        self.geo = self.COUNTRY_GEOS.get(country, "US")
        self.platform = "Google 每日热搜"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = f"https://trends.google.com/trending/rss?geo={self.geo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()

        root = ET.fromstring(res.content)
        items = root.findall(".//item")

        # 命名空间处理
        ns = {"ht": "https://trends.google.com/trending/rss"}

        results = []
        for it in items:
            title_elem = it.find("title")
            link_elem = it.find("link")
            if title_elem is None or not title_elem.text:
                continue

            title = html.unescape(title_elem.text.strip())
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""

            # 搜索量
            traffic_elem = it.find("ht:approx_traffic", ns)
            traffic = traffic_elem.text.strip() if traffic_elem is not None and traffic_elem.text else ""

            # 关联新闻摘要
            news_title_elem = it.find(".//ht:news_item_title", ns)
            news_url_elem = it.find(".//ht:news_item_url", ns)
            news_title = html.unescape(news_title_elem.text.strip()) if news_title_elem is not None and news_title_elem.text else ""
            if news_url_elem is not None and news_url_elem.text:
                link = news_url_elem.text.strip()

            summary = f"关联焦点报道: {news_title}" if news_title else f"Google 趋势搜索指数热度榜"

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=f"热搜量: {traffic}" if traffic else "热门搜索",
                summary=summary
            ))
            if len(results) >= limit:
                break

        return results
