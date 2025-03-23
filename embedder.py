import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

def embed(text):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        res = client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return np.array(res.data[0].embedding, dtype='float32')
    except Exception as e:
        print(f"임베딩 오류: {e}")
        return np.zeros(1536, dtype='float32')
