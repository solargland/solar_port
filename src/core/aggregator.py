import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any

from src.crawlers import (
    NewsItem,
    BaseCrawler,
    WeiboCrawler,
    BaiduCrawler,
    BilibiliCrawler,
    TwitterTrendsCrawler,
    RedditCrawler,
    YahooJapanCrawler,
    GoogleTrendsCrawler,
    GoogleNewsCrawler,
    HackerNewsCrawler,
    RianCrawler,
    TassCrawler,
    LentaCrawler,
)

logger = logging.getLogger("GlobalNewsCrawler")

class NewsAggregator:
    """聚合中枢：调度管理多国多平台爬虫并进行数据归集"""

    def __init__(self):
        # 预设全量多国家主流社交与热榜爬虫矩阵
        self.crawler_registry: List[BaseCrawler] = [
            # 中国 (3个主流平台)
            WeiboCrawler(),
            BaiduCrawler(),
            BilibiliCrawler(),

            # 美国 (4个主流平台与热榜)
            TwitterTrendsCrawler("美国"),
            GoogleNewsCrawler("美国"),
            GoogleTrendsCrawler("美国"),
            RedditCrawler("美国"),

            # 俄罗斯 (3个主流权威与网络热点门户)
            RianCrawler(),
            TassCrawler(),
            LentaCrawler(),

            # 英国 (3个主流平台与热榜)
            TwitterTrendsCrawler("英国"),
            GoogleNewsCrawler("英国"),
            GoogleTrendsCrawler("英国"),

            # 日本 (3个主流平台与热榜)
            YahooJapanCrawler(),
            TwitterTrendsCrawler("日本"),
            GoogleNewsCrawler("日本"),

            # 德国 (3个主流平台与热榜)
            TwitterTrendsCrawler("德国"),
            GoogleNewsCrawler("德国"),
            GoogleTrendsCrawler("德国"),

            # 全球与科技圈 (3个主流平台)
            HackerNewsCrawler(),
            GoogleNewsCrawler("全球"),
            RedditCrawler("全球"),
        ]

    def crawl_all(
        self,
        limit: int = 5,
        selected_countries: Optional[List[str]] = None,
        max_workers: int = 6,
        edition: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        并发抓取所有目标国家与平台的 Top 5 数据
        :param limit: 每个平台抓取前几条，默认 5
        :param selected_countries: 可指定只抓取某些国家，如 ['中国', '美国']
        :param max_workers: 最大并发线程数
        :param edition: 指定早报或晚报 ('早报' / '晚报')，默认自动根据时间判断
        :return: 结构化新闻数据字典
        """
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # 自动判定时段（14点之前为早报，14点之后为晚报）
        if not edition or edition == "auto":
            edition = "早报" if now.hour < 14 else "晚报"

        # 筛选爬虫
        crawlers_to_run = self.crawler_registry
        if selected_countries:
            crawlers_to_run = [c for c in crawlers_to_run if c.country in selected_countries]

        logger.info(f"开始执行全球社交媒体爬取【{edition}】，共激活 {len(crawlers_to_run)} 个数据源...")

        # 结果容器: { country: { platform: [NewsItem, ...] } }
        aggregated_data: Dict[str, Dict[str, List[NewsItem]]] = {}
        total_items_count = 0

        # 线程池并发执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_crawler = {
                executor.submit(crawler.fetch, limit=limit): crawler
                for crawler in crawlers_to_run
            }

            for future in as_completed(future_to_crawler):
                crawler = future_to_crawler[future]
                try:
                    items = future.result()
                    if crawler.country not in aggregated_data:
                        aggregated_data[crawler.country] = {}
                    aggregated_data[crawler.country][crawler.platform] = items
                    total_items_count += len(items)
                    logger.info(f"[{crawler.country} - {crawler.platform}] 成功抓取 {len(items)} 条热点。")
                except Exception as e:
                    logger.error(f"[{crawler.country} - {crawler.platform}] 抓取异常: {e}")
                    if crawler.country not in aggregated_data:
                        aggregated_data[crawler.country] = {}
                    aggregated_data[crawler.country][crawler.platform] = []

        return {
            "title": f"全球主流社交媒体热点聚焦 ({date_str} {edition})",
            "date": date_str,
            "timestamp": time_str,
            "edition": edition,
            "total_items": total_items_count,
            "countries": aggregated_data
        }
