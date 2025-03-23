import os
import faiss
import pandas as pd

def load_index_and_metadata(index_path, meta_path):
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        print("✅ 인덱스 불러옴")
    else:
        index = faiss.IndexFlatL2(1536)
        print("📦 새 인덱스 생성")

    if os.path.exists(meta_path):
        df = pd.read_csv(meta_path)
        print("✅ 메타데이터 불러옴")
    else:
        df = pd.DataFrame(columns=["id", "title", "date", "summary"])
        print("📄 새 메타데이터 생성")

    return index, df

def save_index_and_metadata(index, df, index_path, meta_path):
    faiss.write_index(index, index_path)
    df.to_csv(meta_path, index=False)
    print("💾 저장 완료")
