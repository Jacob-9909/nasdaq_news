import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
client = OpenAI()
# .env 파일에서 API 키 로드
load_dotenv()

# OpenAI API 클라이언트 초기화
openai.api_key = os.getenv("OPENAI_API_KEY")

def translation(text):
    try:
        # OpenAI GPT 모델을 이용하여 번역 요청 (ChatCompletion 사용)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # 또는 gpt-3.5-turbo 모델 사용 가능
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Translate the following text to Korean:\n\n{text}"}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        # 번역된 텍스트 반환
        translated_text = completion.choices[0].message.content.strip()
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return ""
