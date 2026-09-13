from .base import NewsItem, BaseCrawler
from .china import WeiboCrawler, BaiduCrawler, BilibiliCrawler
from .twitter import TwitterTrendsCrawler
from .reddit import RedditCrawler
from .japan import YahooJapanCrawler
from .google_trends import GoogleTrendsCrawler
from .google_news import GoogleNewsCrawler
from .hackernews import HackerNewsCrawler
from .russia import RianCrawler, TassCrawler, LentaCrawler

__all__ = [
    "NewsItem",
    "BaseCrawler",
    "WeiboCrawler",
    "BaiduCrawler",
    "BilibiliCrawler",
    "TwitterTrendsCrawler",
    "RedditCrawler",
    "YahooJapanCrawler",
    "GoogleTrendsCrawler",
    "GoogleNewsCrawler",
    "HackerNewsCrawler",
    "RianCrawler",
    "TassCrawler",
    "LentaCrawler",
]
