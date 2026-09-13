import html
import re
import warnings
from typing import List
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from .base import BaseCrawler, NewsItem

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

class RedditCrawler(BaseCrawler):
    name = "RedditCrawler"

    COUNTRY_SUBREDDITS = {
        "全球": "worldnews",
        "美国": "news",
        "英国": "unitedkingdom",
        "日本": "japan",
        "德国": "de",
        "法国": "france"
    }

    def __init__(self, country: str = "美国", timeout: int = 15):
        super().__init__(timeout=timeout)
        self.country = country
        self.subreddit = self.COUNTRY_SUBREDDITS.get(country, "news")
        self.platform = f"Reddit (r/{self.subreddit})"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        url = f"https://www.reddit.com/r/{self.subreddit}/top/.rss?t=day"
        headers = {
            "User-Agent": "UniversalFeedParser/5.2.1",
            "Accept": "application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8"
        }
        res = self.session.get(url, headers=headers, timeout=self.timeout)
        if res.status_code == 429:
            # 遭遇公共 IP 限流时返回空列表，由其他核心源正常输出
            return []
        res.raise_for_status()

        soup = BeautifulSoup(res.content, "html.parser")
        entries = soup.find_all("entry")

        results = []
        for entry in entries:
            title_elem = entry.find("title")
            link_elem = entry.find("link")
            if not title_elem or not title_elem.text:
                continue

            title = html.unescape(title_elem.text.strip())
            link = link_elem.get("href", "") if link_elem else ""

            author_elem = entry.find("author")
            author = author_elem.find("name").text.strip() if (author_elem and author_elem.find("name")) else "社区热议"

            updated_elem = entry.find("updated")
            updated = updated_elem.text[:10] if (updated_elem and updated_elem.text) else ""

            content_elem = entry.find("content")
            summary_text = ""
            if content_elem and content_elem.text:
                c_soup = BeautifulSoup(content_elem.text, "html.parser")
                text = c_soup.get_text(" ", strip=True)
                summary_text = re.sub(r'\[link\].*?\[comments\]', '', text).strip()
                if len(summary_text) > 150:
                    summary_text = summary_text[:147] + "..."

            results.append(NewsItem(
                country=self.country,
                platform=self.platform,
                rank=len(results) + 1,
                title=title,
                url=link,
                extra=f"发帖人: {author}" + (f" | 日期: {updated}" if updated else ""),
                summary=summary_text
            ))
            if len(results) >= limit:
                break

        return results
