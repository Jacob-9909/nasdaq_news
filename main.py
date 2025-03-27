from config import INDEX_PATH, META_PATH, NEWS_LIMIT
from fetcher import fetch_nasdaq_news, fetch_article_content
from summarizer import summarize
from embedder import embed
from index_manager import save_index_and_metadata
from search import faiss_search
import numpy as np
import pandas as pd
from langchain_community.docstore.in_memory import InMemoryDocstore  # 새로운 임포트
from langchain_community.vectorstores import FAISS
import faiss
from langchain_openai import OpenAIEmbeddings

def run():
    # OpenAI Embedding을 사용하여 임베딩 차원 가져오기
    embedding = OpenAIEmbeddings()
    vector_dim = len(embedding.embed_query("hello world"))  # 벡터 차원

    # FAISS 인덱스 새로 생성
    index = faiss.IndexFlatL2(vector_dim)  # L2 거리 기반 인덱스 생성
    docstore = InMemoryDocstore()  # 새로운 문서 저장소
    index_to_docstore_id = {}  # 빈 딕셔너리로 시작

    # 새로 시작하는 데이터프레임
    df = pd.DataFrame(columns=["id", "title", "date", "summary"])

    # 기사 수집
    articles = fetch_nasdaq_news(limit=NEWS_LIMIT)
    print(f"📰 수집된 기사 수: {len(articles)}")

    # df["date"]를 문자열로 강제 변환 (중복 체크 정확도 향상)
    df["date"] = df["date"].astype(str)

    # 새 문서 임베딩 및 docstore 설정
    new_embeddings = []
    new_rows = []

    # 기존 title+date 조합 키로 중복 체크용 Set 생성
    existing_keys = set((df["title"] + "|" + df["date"]).values)

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
            docstore.add({doc_id: doc_content})  # 새로운 방식으로 문서 추가
            index_to_docstore_id[i] = doc_id  # 인덱스 ID와 문서 ID 매핑

        # 인덱스와 메타데이터 저장
        save_index_and_metadata(index, docstore, index_to_docstore_id, df, INDEX_PATH, META_PATH)
        print(f"\n✅ {len(new_rows)}개의 기사 저장 완료")
    else:
        print("ℹ️ 새로 저장된 기사가 없습니다.")

if __name__ == "__main__":
    run()
