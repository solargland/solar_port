import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from .base import BaseCrawler, NewsItem

class WeiboCrawler(BaseCrawler):
    name = "WeiboCrawler"
    country = "中国"
    platform = "微博热搜"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            "Referer": "https://weibo.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()
        data = res.json()
        raw_items = data.get("data", {}).get("realtime", [])

        results = []
        for it in raw_items:
            # 过滤广告推荐
            if it.get("is_ad"):
                continue
            word = it.get("word", "").strip()
            if not word:
                continue
            
            num = it.get("num", 0)
            tag = it.get("icon_desc", "")
            extra_info = f"热度: {num}" + (f" | {tag}" if tag else "")
            
            link = f"https://s.weibo.com/weibo?q={urllib.parse.quote(word)}"
            item = NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=word,
                url=link,
                extra=extra_info,
                summary=it.get("note", "")
            )
            results.append(item)
            if len(results) >= limit:
                break
        return results

class BaiduCrawler(BaseCrawler):
    name = "BaiduCrawler"
    country = "中国"
    platform = "百度热搜"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://top.baidu.com/board?tab=realtime"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()
        res.encoding = "utf-8"

        soup = BeautifulSoup(res.text, "html.parser")
        wrappers = soup.select(".category-wrap_iQLoo")

        results = []
        for wrap in wrappers:
            title_elem = wrap.select_one(".c-single-text-ellipsis")
            if not title_elem:
                continue
            title = title_elem.text.strip()
            if not title:
                continue

            hot_score_elem = wrap.select_one(".hot-index_1Bl1a")
            hot_score = hot_score_elem.text.strip() if hot_score_elem else ""

            desc_elem = wrap.select_one(".large_nPf-8")
            summary = desc_elem.text.strip() if desc_elem else ""

            link_elem = wrap.select_one("a.img-wrapper_29V76, a.content_1YWBm")
            link = link_elem.get("href") if link_elem and link_elem.get("href") else f"https://www.baidu.com/s?wd={urllib.parse.quote(title)}"

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=f"热搜指数: {hot_score}" if hot_score else "",
                summary=summary
            ))
            if len(results) >= limit:
                break
        return results

class BilibiliCrawler(BaseCrawler):
    name = "BilibiliCrawler"
    country = "中国"
    platform = "哔哩哔哩热搜"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = "https://api.bilibili.com/x/web-interface/search/square?limit=10"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        res.raise_for_status()
        data = res.json()
        raw_items = data.get("data", {}).get("trending", {}).get("list", [])

        results = []
        for it in raw_items[:limit]:
            keyword = it.get("keyword", "").strip()
            show_name = it.get("show_name", keyword).strip()
            title = show_name or keyword
            if not title:
                continue

            icon = it.get("icon", "")
            icon_tag = "热" if "hot" in icon else ("新" if "new" in icon else "")

            link = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(keyword)}"

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=f"标签: {icon_tag}" if icon_tag else "B站热门话题",
                summary=f"Bilibili 搜索实时热门热词榜第 {len(results)+1} 位"
            ))
        return results
