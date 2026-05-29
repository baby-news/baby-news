import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
import hashlib
import time

# ---------- 你的垂直 RSS 源 ----------
# 建议使用自建 RSSHub 实例替换 https://rsshub.app（稳定性更高）
RSSHUB_BASE = "https://rsshub.app"   # 可换成你自己的域名

RSS_SOURCES = [
    # 1. 小红书“育儿”话题（实时热门笔记）
    f"{RSSHUB_BASE}/xiaohongshu/board/育儿",
    # 2. 知乎母婴、育儿类高赞回答
    f"{RSSHUB_BASE}/zhihu/topic/19551137/top-answers",  # 育儿
    f"{RSSHUB_BASE}/zhihu/topic/19642635/top-answers",  # 亲子关系
    f"{RSSHUB_BASE}/zhihu/topic/19770219/top-answers",  # 母婴
    # 3. 微信头部母婴公众号（每日推送）
    f"{RSSHUB_BASE}/wechat/mp/profile/dingxiangmami",   # 丁香妈妈
    f"{RSSHUB_BASE}/wechat/mp/profile/cuiyutao2014",    # 崔玉涛
    f"{RSSHUB_BASE}/wechat/mp/profile/niangao-mama",    # 年糕妈妈
    f"{RSSHUB_BASE}/wechat/mp/profile/babytreemama",    # 宝宝树
    # 4. 可以按关键字继续追加，比如“早教”“辅食”等
]

def fetch_articles():
    articles = []
    seen_links = set()
    
    for url in RSS_SOURCES:
        try:
            # 模拟移动端请求，避免被部分源限制
            feed = feedparser.parse(url, agent='Mozilla/5.0 (Linux; Android 10; K)')
            # 部分源可能需要延迟避免触发反爬
            time.sleep(0.5)
            
            for entry in feed.entries:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                if not title or not link:
                    continue
                
                # 去重
                link_hash = hashlib.md5(link.encode()).hexdigest()
                if link_hash in seen_links:
                    continue
                seen_links.add(link_hash)
                
                # 取来源名
                source = entry.get('source', {}).get('title', '') or feed.feed.get('title', '未知来源')
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                
                articles.append({
                    'title': title,
                    'link': link,
                    'source': source,
                    'published': published
                })
        except Exception as e:
            print(f"抓取失败 {url}: {e}")
            continue

    # 按发布时间倒序，取最新 20 条
    def get_ts(art):
        if art['published']:
            return datetime(*art['published'][:6], tzinfo=timezone.utc).timestamp()
        return 0
    articles.sort(key=get_ts, reverse=True)
    latest = articles[:20]
    
    # 只保留标题、链接、来源
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
    print(f"已更新 {len(items)} 条内容。")

if __name__ == '__main__':
    main()
