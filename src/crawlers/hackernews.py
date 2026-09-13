from typing import List
from .base import BaseCrawler, NewsItem

class HackerNewsCrawler(BaseCrawler):
    name = "HackerNewsCrawler"
    country = "全球科技"
    platform = "Hacker News (科技与商业)"

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        res = self.session.get(top_url, timeout=self.timeout)
        res.raise_for_status()
        ids = res.json()[:limit]

        results = []
        for rank, story_id in enumerate(ids, 1):
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                item_res = self.session.get(story_url, timeout=self.timeout)
                if item_res.status_code != 200:
                    continue
                data = item_res.json()
                title = data.get("title", "")
                url = data.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                score = data.get("score", 0)
                comments = data.get("descendants", 0)
                author = data.get("by", "")

                results.append(NewsItem(
                    country=self.country,
                    platform=self.platform,
                    rank=rank,
                    title=title,
                    url=url,
                    extra=f"点赞: {score} | 评论: {comments} | 发帖人: {author}",
                    summary=f"Hacker News 讨论链接: https://news.ycombinator.com/item?id={story_id}"
                ))
            except Exception:
                continue

        return results
