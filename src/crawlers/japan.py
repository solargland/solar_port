import html
import xml.etree.ElementTree as ET
from typing import List
from .base import BaseCrawler, NewsItem

class YahooJapanCrawler(BaseCrawler):
    name = "YahooJapanCrawler"
    country = "日本"
    platform = "Yahoo! JAPAN 热点要闻"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()

        root = ET.fromstring(res.content)
        items = root.findall(".//item")

        results = []
        for it in items:
            title_elem = it.find("title")
            link_elem = it.find("link")
            pub_date_elem = it.find("pubDate")

            if title_elem is None or not title_elem.text:
                continue

            title = html.unescape(title_elem.text.strip())
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=f"发布时间: {pub_date}" if pub_date else "Yahoo Japan 焦点",
                summary=f"雅虎日本国民级每日焦点关注议题第 {len(results)+1} 位"
            ))
            if len(results) >= limit:
                break

        return results
