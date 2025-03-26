from config import INDEX_PATH, META_PATH, NEWS_LIMIT
from fetcher import fetch_nasdaq_news, fetch_article_content
from summarizer import summarize
from embedder import embed
from index_manager import load_index_and_metadata, save_index_and_metadata
from merge_files import merge_files_from_drive  # 추가된 부분
import numpy as np
import pandas as pd

def run():
    # 0. 기존 인덱스와 메타데이터 파일 로드
    index, df = load_index_and_metadata(INDEX_PATH, META_PATH)  # 기존 인덱스와 메타데이터 로드
    print(f"📰 기존 메타데이터: {len(df)}개의 기사")

    # 1. 뉴스 기사 수집 및 메타데이터 생성
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

    if new_embeddings:
        # 로컬 데이터프레임에 새 데이터 추가
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        # 임베딩을 FAISS 인덱스에 추가
        index.add(np.array(new_embeddings))
        # 메타데이터와 인덱스 저장
        save_index_and_metadata(index, df, INDEX_PATH, META_PATH)
        print(f"\n✅ {len(new_rows)}개의 기사 저장 완료")
    else:
        print("ℹ️ 새로 저장된 기사가 없습니다.")

    # 2. Google Drive에서 메타데이터 및 인덱스 병합 작업
    print("🔄 Google Drive에서 파일을 병합 중...")
    merge_files_from_drive()  # 병합 함수 호출

if __name__ == "__main__":
    run()
