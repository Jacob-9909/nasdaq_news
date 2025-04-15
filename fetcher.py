import requests
from bs4 import BeautifulSoup # type: ignore
from datetime import datetime, timedelta
import email.utils as eut
import pytz

def fetch_nasdaq_news(limit=100):
    rss_urls = [
        "https://www.nasdaq.com/feed/rssoutbound?category=Markets",
        "https://www.nasdaq.com/feed/rssoutbound?symbol=aapl",
        "https://www.nasdaq.com/feed/rssoutbound?symbol=TSLA",
        "https://www.nasdaq.com/feed/rssoutbound?symbol=NVDA",
        "https://www.nasdaq.com/feed/rssoutbound?symbol=MSFT",
        "https://www.nasdaq.com/feed/rssoutbound?category=Stocks",
        "https://www.nasdaq.com/feed/rssoutbound?category=Artificial+Intelligence"]
    
    headers = {"User-Agent": "Mozilla/5.0"}

    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    today_start = now_kst
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_start

    articles = []

    for rss_url in rss_urls:
        try:
            response = requests.get(rss_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print(f"RSS 요청 중 오류 발생 ({rss_url}): {e}")
            continue

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

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
                return articles  # 바로 반환

    return articles

def fetch_article_content(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
    except Exception as e:
        print(f"기사 요청 오류: {e}")
        return "", None

    soup = BeautifulSoup(res.text, 'html.parser')

    # 더 구체적인 본문 선택자 시도
    content_div = (
        soup.select_one("div.body__content") or  # ✅ 나스닥 기사에 실제 사용되는 본문 영역
        soup.select_one("div.article-body") or
        soup.select_one("article") or
        soup.select_one("body")
    )

    if not content_div:
        print("❌ 본문 div를 찾지 못함")
        return "", None

    content = content_div.get_text(separator="\n").strip()
    # 공백 제거
    content = " ".join(content.split())
    # 링크 추출은 생략 가능하거나 그대로 유지
    a_tag = content_div.find("a")
    link = a_tag["href"] if a_tag else None

    return content, link
