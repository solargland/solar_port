import html
import xml.etree.ElementTree as ET
from typing import List
from .base import BaseCrawler, NewsItem

class GoogleNewsCrawler(BaseCrawler):
    name = "GoogleNewsCrawler"

    COUNTRY_PARAMS = {
        "美国": "hl=en-US&gl=US&ceid=US:en",
        "英国": "hl=en-GB&gl=GB&ceid=GB:en",
        "日本": "hl=ja&gl=JP&ceid=JP:ja",
        "德国": "hl=de&gl=DE&ceid=DE:de",
        "法国": "hl=fr&gl=FR&ceid=FR:fr",
        "全球": "headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"
    }

    def __init__(self, country: str = "美国", timeout: int = 15):
        super().__init__(timeout=timeout)
        self.country = country
        self.platform = "主流权威要闻"
        self.param = self.COUNTRY_PARAMS.get(country, "hl=en-US&gl=US&ceid=US:en")

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        if "headlines" in self.param:
            url = f"https://news.google.com/rss/{self.param}"
        else:
            url = f"https://news.google.com/rss?{self.param}"

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
            source_elem = it.find("source")

            if title_elem is None or not title_elem.text:
                continue

            full_title = html.unescape(title_elem.text.strip())
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""
            
            # 提取报道媒体
            source = source_elem.text.strip() if source_elem is not None and source_elem.text else ""
            if not source and " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1]
            else:
                title = full_title

            extra_info = f"媒体: {source}" if source else ""
            if pub_date:
                extra_info += f" | {pub_date[:16]}"

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=extra_info.strip(" |"),
                summary=f"各大权威媒体报道精选（来源: {source or '权威通讯社'}）"
            ))
            if len(results) >= limit:
                break

        return results
