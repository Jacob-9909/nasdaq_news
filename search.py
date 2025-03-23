import numpy as np
from embedder import embed

def faiss_search(index, df):
    query = input("🔍 검색 키워드: ")
    query_vec = embed(query)
    D, I = index.search(np.array([query_vec]), k=1)

    best_index = I[0][0]
    best_article = df.iloc[best_index]

    print(f"\n📌 검색 결과: {best_article['title']}")
    print(f"🗓 날짜: {best_article['date']}")
    print(f"📝 요약: {best_article['summary']}")
