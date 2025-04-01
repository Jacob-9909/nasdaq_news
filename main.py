from config import META_PATH, NEWS_LIMIT
from fetcher import fetch_nasdaq_news, fetch_article_content
from summarizer import summarize
from embedder import translation
from index_manager import save_index_and_metadata
import numpy as np
import pandas as pd

def run():
    # OpenAI Embedding을 사용하여 임베딩 차원 가져오기
    # embedding = OpenAIEmbeddings()
    # vector_dim = 1536

    # # FAISS 벡터 저장소 생성
    # db = FAISS(
    #     embedding_function=embedding,
    #     index=faiss.IndexFlatL2(vector_dim),
    #     docstore=InMemoryDocstore(),
    #     index_to_docstore_id={}
    # )

    # 새로 시작하는 데이터프레임
    df = pd.DataFrame(columns=["id", "title", "date","content","summary"])

    # 기사 수집
    articles = fetch_nasdaq_news(limit=NEWS_LIMIT)
    print(f"📰 수집된 기사 수: {len(articles)}")

    # df["date"]를 문자열로 강제 변환 (중복 체크 정확도 향상)
    df["date"] = df["date"].astype(str)

    # 새 문서 임베딩 및 docstore 설정
    # new_embeddings = []
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

        # # 임베딩 생성
        content = translation(content)
        # new_embeddings.append(vector)
        new_rows.append({
            "id": f"article_{len(df) + len(new_rows) + 1}",
            "title": title,
            "date": date_str,
            "content": content,
            "summary": summary
        })
        # print(content)

    # 새 임베딩 추가 및 인덱스 저장
        # 벡터 추가
        # db.index.add(np.array(new_embeddings))

        # 메타데이터 추가
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

        # # 문서 저장소에 문서 추가 및 매핑
        # for i, row in enumerate(new_rows, start=len(df) - len(new_rows)):
        #     doc_id = f"doc_{i}"
        #     doc_content = row["summary"]
        #     db.docstore.add({doc_id: doc_content})
        #     db.index_to_docstore_id[i] = doc_id

        # 인덱스와 메타데이터 저장
        # save_index_and_metadata( db.index, db.docstore, db.index_to_docstore_id, df, INDEX_PATH, META_PATH)
    save_index_and_metadata(df, META_PATH)
    print(f"\n✅ {len(new_rows)}개의 기사 저장 완료")

if __name__ == "__main__":
    run()
