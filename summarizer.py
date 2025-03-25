import os
from openai import OpenAI
from dotenv import load_dotenv

def summarize(title, content):
    load_dotenv()
    prompt = f"""
제목: {title}
내용: {content[:1000]}

위 뉴스 내용을 5문장 이내로 요약하고, 정세와 시황에 대한 간단한 분석을 해줘.
"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            instructions="너는 미국 나스닥 주식 시장 분석 전문가야.",
            input=prompt,
        )
        return res.output_text.strip()
    except Exception as e:
        print(f"요약 오류: {e}")
        return "요약 실패"
