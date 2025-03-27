from config import INDEX_PATH, META_PATH, NEWS_LIMIT
from fetcher import fetch_nasdaq_news, fetch_article_content
from summarizer import summarize
from embedder import embed
from index_manager import load_index_and_metadata, save_index_and_metadata
from search import faiss_search
import numpy as np
import pandas as pd
from langchain.docstore import InMemoryDocstore

def run():
    # 인덱스와 메타데이터 로드
    index, df = load_index_and_metadata(INDEX_PATH, META_PATH)
    articles = fetch_nasdaq_news(limit=NEWS_LIMIT)
    print(f"📰 수집된 기사 수: {len(articles)}")

    # df["date"]를 문자열로 강제 변환 (중복 체크 정확도 향상)
    df["date"] = df["date"].astype(str)

    # 새 문서 임베딩 및 docstore 설정
    new_embeddings = []
    new_rows = []

    # 기존 title+date 조합 키로 중복 체크용 Set 생성
    existing_keys = set((df["title"] + "|" + df["date"]).values)

    # docstore 및 index_to_docstore_id 초기화
    docstore = InMemoryDocstore({})  # 빈 문서 저장소 생성
    index_to_docstore_id = {}

    # 기존 title+date를 기반으로 docstore 및 인덱스 ID 매핑 설정
    for idx, row in df.iterrows():
        doc_id = f"doc_{idx}"
        doc_content = row['summary']  # 예시로 summary를 원본 텍스트로 사용
        docstore.add_document(doc_id, doc_content)  # docstore에 원본 문서 추가
        index_to_docstore_id[idx] = doc_id  # 인덱스 ID와 문서 ID 매핑

    # 기사 처리 및 임베딩 추가
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

        # 임베딩 생성
        vector = embed(f"{title}\n{summary}")
        new_embeddings.append(vector)
        new_rows.append({
            "id": f"article_{len(df) + len(new_rows) + 1}",
            "title": title,
            "date": date_str,
            "summary": summary
        })

    # 새 임베딩 추가 및 인덱스 저장
    if new_embeddings:
        # FAISS 인덱스에 벡터 추가
        index.add(np.array(new_embeddings))
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)  # 메타데이터 추가

        # 새 문서 정보 docstore에 추가
        for i, row in enumerate(new_rows, start=len(df) - len(new_rows)):
            doc_id = f"doc_{i}"
            doc_content = row["summary"]
            docstore.add_document(doc_id, doc_content)  # docstore에 원본 문서 추가
            index_to_docstore_id[i] = doc_id  # 인덱스 ID와 문서 ID 매핑

        # 인덱스와 메타데이터 저장
        save_index_and_metadata(index, df, INDEX_PATH, META_PATH)
        print(f"\n✅ {len(new_rows)}개의 기사 저장 완료")
    else:
        print("ℹ️ 새로 저장된 기사가 없습니다.")

    # faiss_search(index, df)  # 추가적으로 검색 기능을 사용하려면 여기를 활성화

if __name__ == "__main__":
    run()
