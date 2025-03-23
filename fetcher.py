import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import email.utils as eut
import pytz

def fetch_nasdaq_news(limit=5):
    rss_url = "https://www.nasdaq.com/feed/rssoutbound?category=Markets"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"RSS 요청 중 오류 발생: {e}")
        return []

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    today_start = now_kst
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_start

    articles = []
    for item in items:
        title_tag = item.find("title")
        link_tag = item.find("link")
        pub_date_tag = item.find("pubDate")
        if not (title_tag and link_tag and pub_date_tag):
            continue

        pub_date_utc = eut.parsedate_to_datetime(pub_date_tag.get_text())
        pub_date_kst = pub_date_utc.astimezone(kst)

        if not (yesterday_start <= pub_date_kst < yesterday_end):
            continue

        articles.append({
            "title": title_tag.get_text(strip=True),
            "url": link_tag.get_text(strip=True),
            "pub_date": pub_date_kst.isoformat()
        })

        if len(articles) >= limit:
            break

    return articles

def fetch_article_content(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
    except Exception as e:
        print(f"기사 요청 오류: {e}")
        return "", None

    soup = BeautifulSoup(res.text, 'html.parser')
    content_div = soup.select_one("div.article-body") or soup.select_one("body")
    content = content_div.get_text(separator="\n").strip()
    a_tag = content_div.find("a")
    link = a_tag["href"] if a_tag else None
    return content, link
