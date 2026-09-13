import os
import html
import json
from typing import Dict, Any

class HTMLReporter:
    """现代化响应式单文件 HTML 仪表盘生成器"""

    def __init__(self, output_dir: str = "daily_reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def render(self, data: Dict[str, Any]) -> str:
        date_str = data.get("date", "")
        timestamp = data.get("timestamp", "")
        edition = data.get("edition", "热点")
        total_items = data.get("total_items", 0)
        countries_data = data.get("countries", {})

        # 序列化为 JSON 便于前端搜索与筛选
        serializable_data = {}
        for country, platforms in countries_data.items():
            serializable_data[country] = {}
            for platform, items in platforms.items():
                serializable_data[country][platform] = [item.to_dict() for item in items]

        json_dump = json.dumps(serializable_data, ensure_ascii=False)

        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🌍 全球主流社交媒体【{edition}】({date_str})</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: rgba(30, 41, 59, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-gradient: linear-gradient(135deg, #38bdf8, #818cf8);
      --gold: #fbbf24;
      --silver: #cbd5e1;
      --bronze: #f97316;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      background-color: var(--bg);
      background-image: radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
                        radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.1) 0px, transparent 50%);
      color: var(--text-main);
      min-height: 100vh;
      padding: 2rem 1rem;
      line-height: 1.6;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    header {{
      text-align: center;
      margin-bottom: 2.5rem;
      padding: 2rem 1rem;
      background: var(--card-bg);
      border-radius: 16px;
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px);
    }}
    header h1 {{
      font-size: 2.2rem;
      font-weight: 800;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.8rem;
    }}
    .meta-bar {{
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      flex-wrap: wrap;
      color: var(--text-muted);
      font-size: 0.95rem;
    }}
    .meta-badge {{
      display: inline-flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.05);
      padding: 0.3rem 0.8rem;
      border-radius: 9999px;
      border: 1px solid var(--card-border);
    }}
    .controls {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .search-box {{
      width: 100%;
      padding: 0.85rem 1.25rem;
      border-radius: 12px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-main);
      font-size: 1rem;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-box:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
    }}
    .filter-tabs {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    .tab-btn {{
      padding: 0.5rem 1.1rem;
      border-radius: 8px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn:hover, .tab-btn.active {{
      background: var(--accent);
      color: #0f172a;
      font-weight: 600;
      border-color: var(--accent);
    }}
    .country-section {{
      margin-bottom: 3rem;
    }}
    .country-title {{
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 1.2rem;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      border-left: 4px solid var(--accent);
      padding-left: 0.8rem;
    }}
    .platforms-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 1.5rem;
    }}
    .platform-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      backdrop-filter: blur(10px);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }}
    .platform-header {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 1rem;
      padding-bottom: 0.6rem;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .news-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }}
    .news-item {{
      display: flex;
      gap: 0.8rem;
      align-items: flex-start;
      padding: 0.5rem 0.6rem;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.02);
      transition: background 0.2s, transform 0.2s;
    }}
    .news-item:hover {{
      background: rgba(255, 255, 255, 0.06);
      transform: translateX(4px);
    }}
    .rank-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      border-radius: 6px;
      font-weight: 800;
      font-size: 0.85rem;
      flex-shrink: 0;
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-muted);
    }}
    .rank-1 {{ background: var(--gold); color: #000; box-shadow: 0 0 10px rgba(251, 191, 36, 0.4); }}
    .rank-2 {{ background: var(--silver); color: #000; }}
    .rank-3 {{ background: var(--bronze); color: #fff; }}
    .news-content {{
      flex: 1;
      min-width: 0;
    }}
    .news-title {{
      color: var(--text-main);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
      word-break: break-word;
      display: block;
      transition: color 0.2s;
    }}
    .news-title:hover {{
      color: var(--accent);
      text-decoration: underline;
    }}
    .news-extra {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
    }}
    .news-summary {{
      font-size: 0.8rem;
      color: #94a3b8;
      margin-top: 0.3rem;
      border-left: 2px solid rgba(255, 255, 255, 0.1);
      padding-left: 0.5rem;
    }}
    footer {{
      text-align: center;
      margin-top: 4rem;
      color: var(--text-muted);
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🌍 全球主流社交媒体【{edition}】Top 5</h1>
      <div class="meta-bar">
        <span class="meta-badge">📅 日期: {date_str}</span>
        <span class="meta-badge">⏰ 采集时间: {timestamp} ({edition})</span>
        <span class="meta-badge">📊 总归集条目: {total_items}</span>
      </div>
    </header>

    <div class="controls">
      <input type="text" id="searchInput" class="search-box" placeholder="🔍 搜索热搜话题、国家、平台或关键词...">
      <div class="filter-tabs" id="filterTabs">
        <button class="tab-btn active" data-filter="all">全部国家/区域</button>
      </div>
    </div>

    <main id="newsContainer"></main>

    <footer>
      <p>© {date_str[:4]} Global Daily Social News Crawler • 自动调度生成</p>
    </footer>
  </div>

  <script>
    const rawData = {json_dump};
    let currentFilter = 'all';
    let searchQuery = '';

    const countryIcons = {{
      '中国': '🇨🇳',
      '俄罗斯': '🇷🇺',
      '美国': '🇺🇸',
      '英国': '🇬🇧',
      '日本': '🇯🇵',
      '德国': '🇩🇪',
      '法国': '🇫🇷',
      '全球科技': '🌐',
      '全球': '🌍'
    }};

    function initFilters() {{
      const filterTabs = document.getElementById('filterTabs');
      const countries = Object.keys(rawData);
      countries.forEach(c => {{
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.dataset.filter = c;
        btn.textContent = (countryIcons[c] || '🌐') + ' ' + c;
        btn.onclick = () => {{
          document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentFilter = c;
          render();
        }};
        filterTabs.appendChild(btn);
      }});

      document.querySelector('[data-filter="all"]').onclick = function() {{
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentFilter = 'all';
        render();
      }};

      document.getElementById('searchInput').addEventListener('input', (e) => {{
        searchQuery = e.target.value.toLowerCase().trim();
        render();
      }});
    }}

    function render() {{
      const container = document.getElementById('newsContainer');
      container.innerHTML = '';

      const countries = Object.keys(rawData).filter(c => currentFilter === 'all' || currentFilter === c);

      countries.forEach(country => {{
        const platforms = rawData[country];
        let countryHasMatch = false;

        const countrySection = document.createElement('section');
        countrySection.className = 'country-section';

        const title = document.createElement('h2');
        title.className = 'country-title';
        title.innerHTML = `<span>${{countryIcons[country] || '🌐'}}</span> <span>${{country}} 热门社交媒体</span>`;

        const grid = document.createElement('div');
        grid.className = 'platforms-grid';

        Object.keys(platforms).forEach(platform => {{
          const items = platforms[platform];
          const matchedItems = items.filter(it => {{
            if (!searchQuery) return true;
            return it.title.toLowerCase().includes(searchQuery) ||
                   (it.extra && it.extra.toLowerCase().includes(searchQuery)) ||
                   (it.summary && it.summary.toLowerCase().includes(searchQuery)) ||
                   platform.toLowerCase().includes(searchQuery) ||
                   country.toLowerCase().includes(searchQuery);
          }});

          if (matchedItems.length > 0) {{
            countryHasMatch = true;
            const card = document.createElement('div');
            card.className = 'platform-card';

            const header = document.createElement('div');
            header.className = 'platform-header';
            header.innerHTML = `<span>${{platform}}</span> <small style="color: var(--text-muted); font-size: 0.8rem;">Top ${{matchedItems.length}}</small>`;
            card.appendChild(header);

            const ul = document.createElement('ul');
            ul.className = 'news-list';

            matchedItems.forEach(it => {{
              const li = document.createElement('li');
              li.className = 'news-item';
              const rankClass = it.rank <= 3 ? `rank-${{it.rank}}` : '';

              li.innerHTML = `
                <div class="rank-badge ${{rankClass}}">${{it.rank}}</div>
                <div class="news-content">
                  <a href="${{it.url}}" target="_blank" rel="noopener noreferrer" class="news-title">${{it.title}}</a>
                  ${{it.extra ? `<div class="news-extra">${{it.extra}}</div>` : ''}}
                  ${{it.summary ? `<div class="news-summary">${{it.summary}}</div>` : ''}}
                </div>
              `;
              ul.appendChild(li);
            }});

            card.appendChild(ul);
            grid.appendChild(card);
          }}
        }});

        if (countryHasMatch) {{
          countrySection.appendChild(title);
          countrySection.appendChild(grid);
          container.appendChild(countrySection);
        }}
      }});

      if (container.children.length === 0) {{
        container.innerHTML = `<div style="text-align:center; padding: 4rem; color: var(--text-muted);">未找到符合条件的搜索结果。</div>`;
      }}
    }}

    initFilters();
    render();
  </script>
</body>
</html>
"""
        return html_template

    def save(self, data: Dict[str, Any]) -> str:
        content = self.render(data)
        date_str = data.get("date", "latest")
        edition = data.get("edition", "热点")
        filepath = os.path.join(self.output_dir, f"{date_str}_{edition}_global_social_news.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.abspath(filepath)

    def render_email(self, data: Dict[str, Any]) -> str:
        """专门为邮件客户端（如手机 QQ 邮箱）优化的纯静态 HTML，不依赖 JS"""
        date_str = data.get("date", "")
        timestamp = data.get("timestamp", "")
        edition = data.get("edition", "热点")
        total_items = data.get("total_items", 0)
        countries_data = data.get("countries", {})

        country_icons = {
            "中国": "🇨🇳",
            "俄罗斯": "🇷🇺",
            "美国": "🇺🇸",
            "英国": "🇬🇧",
            "日本": "🇯🇵",
            "德国": "🇩🇪",
            "法国": "🇫🇷",
            "全球科技": "🌐",
            "全球": "🌍"
        }
        platform_icons = {
            "微博热搜": "🔥",
            "百度热搜": "🔍",
            "哔哩哔哩热搜": "📺",
            "俄新社 (RIA Novosti)": "🇷🇺",
            "塔斯社 (TASS)": "📡",
            "Lenta.ru (俄罗斯门户热榜)": "🔥",
            "X (Twitter) 趋势": "🐦",
            "Yahoo! JAPAN 热点要闻": "🇯🇵",
            "Google 每日热搜": "🔎",
            "Hacker News (科技与商业)": "💻",
            "主流权威要闻": "📰",
        }

        sections_html = []
        for country, platforms in sorted(countries_data.items()):
            has_items = any(len(items) > 0 for items in platforms.values())
            if not has_items:
                continue

            c_icon = country_icons.get(country, "🌐")
            cards_html = []

            for platform, items in platforms.items():
                if not items:
                    continue
                p_icon = platform_icons.get(platform, "📌")

                items_rows = []
                for it in items:
                    rank = it.rank
                    if rank == 1:
                        badge_style = "background:#fbbf24;color:#000;font-weight:bold;display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:4px;font-size:12px;"
                    elif rank == 2:
                        badge_style = "background:#cbd5e1;color:#000;font-weight:bold;display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:4px;font-size:12px;"
                    elif rank == 3:
                        badge_style = "background:#f97316;color:#fff;font-weight:bold;display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:4px;font-size:12px;"
                    else:
                        badge_style = "background:rgba(255,255,255,0.15);color:#94a3b8;font-weight:bold;display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:4px;font-size:12px;"

                    extra_html = f'<div style="font-size:12px;color:#94a3b8;margin-top:2px;">{html.escape(it.extra)}</div>' if it.extra else ""
                    summary_html = f'<div style="font-size:12px;color:#cbd5e1;margin-top:4px;padding-left:8px;border-left:2px solid #475569;line-height:1.4;">{html.escape(it.summary)}</div>' if it.summary else ""

                    row = f"""
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                      <td style="width:28px;vertical-align:top;padding:10px 0;">
                        <span style="{badge_style}">{rank}</span>
                      </td>
                      <td style="padding:10px 0 10px 8px;vertical-align:top;">
                        <a href="{it.url}" target="_blank" style="color:#38bdf8;text-decoration:none;font-weight:600;font-size:15px;line-height:1.4;display:block;">{html.escape(it.title)}</a>
                        {extra_html}
                        {summary_html}
                      </td>
                    </tr>
                    """
                    items_rows.append(row)

                card_html = f"""
                <div style="background:#1e293b;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 16px;margin-bottom:16px;">
                  <div style="font-size:15px;font-weight:700;color:#38bdf8;padding-bottom:8px;margin-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.08);">
                    {p_icon} {html.escape(platform)} <span style="font-size:12px;color:#94a3b8;font-weight:normal;float:right;">Top {len(items)}</span>
                  </div>
                  <table style="width:100%;border-collapse:collapse;">
                    {''.join(items_rows)}
                  </table>
                </div>
                """
                cards_html.append(card_html)

            country_block = f"""
            <div style="margin-bottom:28px;">
              <h2 style="font-size:17px;font-weight:700;color:#f8fafc;margin:0 0 12px 0;padding-left:8px;border-left:4px solid #38bdf8;">
                {c_icon} {html.escape(country)} 社交热点
              </h2>
              {''.join(cards_html)}
            </div>
            """
            sections_html.append(country_block)

        email_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>【全球社交{edition}】{date_str}</title>
</head>
<body style="margin:0;padding:16px 8px;background-color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#f8fafc;line-height:1.5;">
  <div style="max-width:680px;margin:0 auto;background-color:#0f172a;">
    
    <!-- 头部卡片 -->
    <div style="background:#1e293b;border:1px solid rgba(56,189,248,0.3);border-radius:16px;padding:22px 16px;text-align:center;margin-bottom:22px;">
      <h1 style="margin:0 0 8px 0;font-size:22px;color:#38bdf8;font-weight:800;">
        🌍 全球主流社交媒体【{edition}】Top 5
      </h1>
      <div style="font-size:13px;color:#94a3b8;line-height:1.8;">
        📅 日期: <strong style="color:#f8fafc;">{date_str}</strong> &nbsp;|&nbsp; 
        ⏰ 采集时间: <strong style="color:#f8fafc;">{timestamp}</strong><br>
        📊 本期共归集: <strong style="color:#38bdf8;">{total_items}</strong> 条世界前沿舆论动态
      </div>
      <div style="margin-top:12px;display:inline-block;padding:4px 12px;background:rgba(56,189,248,0.1);border-radius:20px;font-size:12px;color:#38bdf8;">
        💡 点击各热点标题可直接跳转至原社交平台或报道
      </div>
    </div>

    <!-- 各国热点主体内容 (纯静态渲染，邮件端 100% 直读) -->
    {''.join(sections_html)}

    <!-- 页脚 -->
    <div style="text-align:center;padding:24px 0;color:#64748b;font-size:12px;border-top:1px solid rgba(255,255,255,0.08);margin-top:20px;">
      © {date_str[:4]} solar_port • 全球社交热点自动调度生成
    </div>
  </div>
</body>
</html>
"""
        return email_html
