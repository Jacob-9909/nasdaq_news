import os
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import pandas as pd

def save_index_and_metadata(index, docstore, index_to_docstore_id, df, index_path, meta_path):
    """
    FAISS 인덱스, 문서 저장소, 그리고 인덱스와 문서 ID 매핑을 지정된 경로에 저장합니다.
    """

    # FAISS 벡터 스토어 설정
    vector_store = FAISS(
        embedding_function=None,  # 임베딩 함수는 나중에 지정 가능
        index=index,              # FAISS 인덱스
        docstore=docstore,        # 문서 저장소
        index_to_docstore_id=index_to_docstore_id  # 인덱스 ID와 문서 ID 매핑
    )

    # 메타데이터를 CSV로 저장
    df.to_csv(meta_path, index=False)

    # FAISS 벡터 스토어 저장
    vector_store.save_local(index_path)
    print("💾 저장 완료")


