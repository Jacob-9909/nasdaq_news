import os
from datetime import datetime

# 오늘 날짜를 "YYYY-MM-DD" 형식으로 가져옵니다
today_date = datetime.now().strftime("%Y-%m-%d")

# 날짜를 포함한 파일 경로로 설정
INDEX_PATH = f"nasdaq_index_{today_date}.faiss"
META_PATH = f"nasdaq_metadata_{today_date}.csv"
NEWS_LIMIT = 50