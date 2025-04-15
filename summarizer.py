import os
from openai import OpenAI
from dotenv import load_dotenv

def summarize(title, content):
    load_dotenv()
    
    # 요약할 텍스트 생성
    prompt = f"""
제목: {title}
내용: {content[:2000]}

위 뉴스 내용을 5문장 이내로 요약하고, 간단한 분석을 해줘.
"""
    
    # OpenAI API 클라이언트 생성
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # GPT 모델을 이용하여 요약 및 분석 요청 (chat.completions.create 사용)
        completion = client.chat.completions.create(
            model="gpt-4",  # gpt-4 모델 사용
            messages=[
                {"role": "system", "content": "너는 주식 시장 분석 전문가야"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # 출력 길이 제한 (조정 가능)
            temperature=0.5    # 다소 창의적인 답변을 유도
        )
        
        # 결과에서 요약된 텍스트 추출
        summary = completion.choices[0].message['content'].strip()
        return summary
    
    except Exception as e:
        print(f"요약 오류: {e}")
        return "요약 실패"

