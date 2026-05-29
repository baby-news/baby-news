import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
import hashlib

# 多个RSS源（母婴、亲子、育儿）
RSS_SOURCES = [
    # Google News 中文育儿
    "https://news.google.com/rss/search?q=%E8%82%B2%E5%84%BF%20OR%20%E6%AF%8D%E5%A9%B4%20OR%20%E4%BA%B2%E5%AD%90&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    # 也可添加其他可靠源，例如新浪育儿RSS（如果有稳定RSS）
    # "https://rsshub.app/sina/baby",  # 需要RSSHub实例，可自行搭建
    # 丁香妈妈（暂无可直接使用的RSS，可后续补充）
]

def fetch_articles():
    articles = []
    seen_links = set()
    
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url, agent='Mozilla/5.0')
            for entry in feed.entries:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                if not title or not link:
                    continue
                # 去重（基于链接哈希）
                link_hash = hashlib.md5(link.encode()).hexdigest()
                if link_hash in seen_links:
                    continue
                seen_links.add(link_hash)
                
                source = entry.get('source', {}).get('title', '') or feed.feed.get('title', '未知来源')
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                articles.append({
                    'title': title,
                    'link': link,
                    'source': source,
                    'published': published
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    # 按发布时间倒序，取最新20条
    def get_ts(art):
        if art['published']:
            return datetime(*art['published'][:6], tzinfo=timezone.utc).timestamp()
        return 0
    articles.sort(key=get_ts, reverse=True)
    latest = articles[:20]
    
    # 精简输出
    output = []
    for art in latest:
        output.append({
            'title': art['title'],
            'link': art['link'],
            'source': art['source']
        })
    return output

def main():
    items = fetch_articles()
    result = {
        'update_time': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'items': items
    }
    with open('hot.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Updated {len(items)} items.")

if __name__ == '__main__':
    main()
