import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("GlobalNewsCrawler")

@dataclass
class NewsItem:
    country: str          # 国家/地区，如 "中国", "美国", "日本", "英国"
    platform: str         # 平台名称，如 "微博", "Twitter/X", "Reddit", "Yahoo Japan"
    rank: int             # 排名 1-5
    title: str            # 标题或话题名称
    url: str              # 跳转链接
    extra: str = ""       # 附加信息：如热度指数、点赞数、分类标签等
    summary: str = ""     # 简要摘要或描述

    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "platform": self.platform,
            "rank": self.rank,
            "title": self.title,
            "url": self.url,
            "extra": self.extra,
            "summary": self.summary
        }

class BaseCrawler:
    name: str = "BaseCrawler"
    country: str = "Global"
    platform: str = "Unknown"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    }

    def __init__(self, timeout: int = 15, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        """抓取前 limit 条数据，并在发生网络错误时自动重试"""
        for attempt in range(1, self.max_retries + 1):
            try:
                items = self._crawl(limit=limit)
                # 保证最多只取前 limit 条并矫正 rank
                valid_items = []
                for i, item in enumerate(items[:limit], 1):
                    item.rank = i
                    valid_items.append(item)
                return valid_items
            except Exception as e:
                logger.warning(f"[{self.country} - {self.platform}] 第 {attempt} 次抓取失败: {e}")
                if attempt < self.max_retries:
                    time.sleep(1.5 * attempt)
                else:
                    logger.error(f"[{self.country} - {self.platform}] 重试超限，抓取终止。")
        return []

    def _crawl(self, limit: int = 5) -> List[NewsItem]:
        raise NotImplementedError("子类必须实现 _crawl 方法")
