import html
import xml.etree.ElementTree as ET
from typing import List
from .base import BaseCrawler, NewsItem

class RianCrawler(BaseCrawler):
    name = "RianCrawler"
    country = "俄罗斯"
    platform = "俄新社 (RIA Novosti)"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://ria.ru/export/rss2/index.xml"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
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
                extra=f"发布时间: {pub_date[:16]}" if pub_date else "俄新社最新要闻",
                summary="俄罗斯国家通讯社（俄新社）实时焦点"
            ))
            if len(results) >= limit:
                break

        return results

class TassCrawler(BaseCrawler):
    name = "TassCrawler"
    country = "俄罗斯"
    platform = "塔斯社 (TASS)"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://tass.ru/rss/v2.xml"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()

        root = ET.fromstring(res.content)
        items = root.findall(".//item")

        results = []
        for it in items:
            title_elem = it.find("title")
            link_elem = it.find("link")
            desc_elem = it.find("description")

            if title_elem is None or not title_elem.text:
                continue

            title = html.unescape(title_elem.text.strip())
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            summary = html.unescape(desc_elem.text.strip()) if desc_elem is not None and desc_elem.text else ""
            if len(summary) > 120:
                summary = summary[:117] + "..."

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra="塔斯社国家通讯社",
                summary=summary or "俄罗斯塔斯社焦点要闻报道"
            ))
            if len(results) >= limit:
                break

        return results

class LentaCrawler(BaseCrawler):
    name = "LentaCrawler"
    country = "俄罗斯"
    platform = "Lenta.ru (俄罗斯门户热榜)"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://lenta.ru/rss/top7"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()

        root = ET.fromstring(res.content)
        items = root.findall(".//item")

        results = []
        for it in items:
            title_elem = it.find("title")
            link_elem = it.find("link")
            category_elem = it.find("category")

            if title_elem is None or not title_elem.text:
                continue

            title = html.unescape(title_elem.text.strip())
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            category = category_elem.text.strip() if category_elem is not None and category_elem.text else ""

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=f"分类: {category}" if category else "俄语第一大热榜门户",
                summary=f"Lenta.ru 俄罗斯全网高关注度热点第 {len(results)+1} 位"
            ))
            if len(results) >= limit:
                break

        return results
