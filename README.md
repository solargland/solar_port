# 🌍 全球主流国家社交媒体每日热点爬虫 (Global Daily News Crawler)

每天自动抓取中国、美国、英国、日本、德国等主流国家的各个主流社交媒体与舆论平台**前五条**实时热点新闻，一键生成精美 Markdown 日报与单文件响应式 HTML 可视化看板，并支持邮件自动推送。

---

## 📌 支持的国家与主流社交平台

| 国家 / 区域 | 社交平台 / 舆论源 | 抓取内容与特点 |
| :--- | :--- | :--- |
| 🇨🇳 **中国** | **微博** (`Weibo`) | 实时热搜榜 Top 5，含热度值与分类标签 |
| 🇨🇳 **中国** | **百度** (`Baidu`) | 实时热搜榜 Top 5，含热搜指数与摘要 |
| 🇨🇳 **中国** | **Bilibili** (`B站`) | 全站全天热门榜 Top 5，含播放量与 UP 主 |
| 🇺🇸 **美国 / 全球** | **X (Twitter)** | 实时 Twitter 热门趋势 Top 5（基于 Trends24 稳定解析） |
| 🇺🇸 **美国 / 全球** | **Reddit** (`r/news`, `r/worldnews`) | 每日高赞讨论帖与突发外链新闻 Top 5 |
| 🇺🇸 **美国 / 全球** | **Google Trends (US)** | 每日热搜榜 Top 5，含指数与关联新闻 |
| 🇬🇧 **英国** | **X (Twitter UK)** | 英国实时趋势 Top 5 |
| 🇬🇧 **英国** | **Reddit UK** (`r/unitedkingdom`) | 英国社区每日精选热帖 Top 5 |
| 🇬🇧 **英国** | **Google Trends (UK)** | 英国每日热搜词榜 Top 5 |
| 🇯🇵 **日本** | **Yahoo! JAPAN** | 日本国民级焦点要闻榜 Top 5 |
| 🇯🇵 **日本** | **X (Twitter Japan)** | 日本实时推特趋势榜 Top 5 |
| 🇯🇵 **日本** | **Reddit Japan** (`r/japan`) | 日本焦点与国际视点 Top 5 |
| 🇩🇪 **德国** | **X (Twitter DE) & Reddit DE** | 德国实时推特趋势与 `r/de` 热门 Top 5 |
| 🌐 **全球科技** | **Hacker News (HN)** | 全球技术与极客商业热榜 Top 5，含得分与讨论数 |

---

## 🚀 快速上手

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 执行一次全量抓取与生成
```bash
python main.py
```
> 执行完成后，将在 `daily_reports/` 目录下生成：
> - `YYYY-MM-DD_global_social_news.md`：排版美观的 Markdown 日报
> - `YYYY-MM-DD_global_social_news.html`：支持**关键词搜索**、**国家一键筛选**的响应式交互看板

### 3. 带邮件自动推送
如需将日报自动发送至邮箱，请确保 `report/mail_config.json` 中的配置有效，随后运行：
```bash
python main.py --send-email
```

### 4. 更多命令行参数
```bash
# 只抓取中国和美国
python main.py --country 中国,美国

# 每平台抓取前 3 条（默认 5 条）
python main.py --limit 3

# 测试各源连通性 (Dry Run)
python main.py --dry-run
```

---

## ⏰ 每日自动化定时运行

### 方案 A：注册为 Windows 原生系统定时任务（推荐，无需常驻黑窗口）
以管理员身份打开终端，运行：
```bash
python scheduler.py --register-windows-task --time 08:30
```
- 系统将在**每天早晨 08:30** 静默拉起爬虫并自动发送邮件提醒。
- 如需取消，运行 `python scheduler.py --unregister-windows-task` 即可。

### 方案 B：常驻后台循环守护
```bash
python scheduler.py --time 08:30
```

### 方案 C：GitHub Actions 云端全自动执行并发送邮件（零本地资源消耗）
仓库已内置并配置好 [.github/workflows/daily_crawler.yml](.github/workflows/daily_crawler.yml)，每天北京时间早上 08:00 自动在云端执行爬虫、将报告发送至您的邮箱，并自动 commit 归档历史日报。

**配置步骤（只需 1 分钟）：**
1. 将本项目推送到您的 GitHub 仓库（公开或私有仓库均可）。
2. 在 GitHub 仓库页面点击 **Settings** -> 展开左侧 **Secrets and variables** -> 点击 **Actions**。
3. 点击 **New repository secret** 分别添加以下 3 个机密变量：
   - `SENDER_EMAIL`：发件 QQ 邮箱（例如 `2549862146@qq.com`）
   - `AUTH_CODE`：QQ 邮箱 16 位 SMTP 授权码（在 QQ 邮箱网页版设置 -> 账户中生成）
   - `RECEIVER_EMAIL`：接收日报的邮箱（例如 `2549862146@qq.com`）
4. （可选）测试触发：点击仓库顶部的 **Actions** 标签 -> 选择 **Daily Global Social News Crawler** -> 点击右侧 **Run workflow** 即可立即在云端测试运行并收到邮件！

---

## 📁 目录结构

```
to_project4/
├── main.py                     # 主程序入口
├── scheduler.py                # 定时调度与 Windows 计划任务工具
├── requirements.txt            # Python 依赖清单
├── daily_reports/              # 每日生成的 Markdown 与 HTML 报告目录
│   ├── 2026-09-13_global_social_news.md
│   └── 2026-09-13_global_social_news.html
├── src/
│   ├── crawlers/               # 各国各平台爬虫实现
│   │   ├── base.py             # 爬虫基类与 NewsItem 数据模型
│   │   ├── china.py            # 微博、百度、B站
│   │   ├── twitter.py          # 美、英、日、德、法 Twitter/X 趋势
│   │   ├── reddit.py           # 美、英、日、德 Reddit 社区热点
│   │   ├── japan.py            # Yahoo Japan 焦点新闻
│   │   ├── google_trends.py    # Google Trends 各国搜索热度
│   │   └── hackernews.py       # Hacker News 科技热点
│   ├── core/
│   │   └── aggregator.py       # 多源并发调度与数据聚合中枢
│   ├── reporters/
│   │   ├── markdown_reporter.py# Markdown 日报渲染器
│   │   └── html_reporter.py    # 单文件 HTML 仪表盘渲染器
│   └── notifier/
│       └── email_sender.py     # 邮件推送通知模块
└── .github/
    └── workflows/
        └── daily_crawler.yml   # GitHub Actions 每日自动化工作流
```
