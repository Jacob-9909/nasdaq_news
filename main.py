import pandas as pd
import numpy as np
import faiss
from config import INDEX_PATH, META_PATH, NEWS_LIMIT
from fetcher import fetch_nasdaq_news, fetch_article_content
from summarizer import summarize
from embedder import embed
from index_manager import load_index_and_metadata, save_index_and_metadata

def run():
    # 기존 인덱스와 메타데이터 불러오기
    index, df = load_index_and_metadata(INDEX_PATH, META_PATH)

    articles = fetch_nasdaq_news(limit=NEWS_LIMIT)
    print(f"📰 수집된 기사 수: {len(articles)}")

    # df["date"]를 문자열로 강제 변환 (중복 체크 정확도 향상)
    df["date"] = df["date"].astype(str)

    new_embeddings = []
    new_rows = []

    # 기존 title+date 조합 키로 중복 체크용 Set 생성
    existing_keys = set((df["title"] + "|" + df["date"]).values)

    for idx, article in enumerate(articles, start=1):
        raw_title = article["title"]
        date_str = article["pub_date"][:10]  # YYYY-MM-DD
        title = f"{raw_title} [{date_str}]"  # 제목 + 날짜 조합
        url = article["url"]

        # 중복 검사 (title + date 문자열 기준)
        key = f"{title}|{date_str}"
        if key in existing_keys:
            print(f"⚠️ 중복 기사 스킵: {title}")
            continue

        print(f"\n[{idx}] {title}")
        print(f"📄 URL: {url}")
        content, _ = fetch_article_content(url)
        if not content:
            print("❌ 본문 수집 실패")
            continue

        summary = summarize(title, content)
        print("📝 요약 완료")

        vector = embed(f"{title}\n{summary}")
        new_embeddings.append(vector)
        new_rows.append({
            "id": f"article_{len(df) + len(new_rows) + 1}",
            "title": title,
            "date": date_str,
            "summary": summary
        })

    # 새로 수집된 데이터가 있으면 인덱스에 추가하고 데이터프레임에 이어붙임
    if new_embeddings:

        index.add(np.array(new_embeddings))
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)

        save_index_and_metadata(index, df, INDEX_PATH, META_PATH)
        print(f"\n✅ {len(new_rows)}개의 기사 저장 완료")
    else:
        print("ℹ️ 새로 저장된 기사가 없습니다.")

if __name__ == "__main__":
    run()
