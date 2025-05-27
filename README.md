# Nasdaq News Summarizer & Automation

GitHub Actions를 이용하여 나스닥 뉴스를 자동으로 수집, 요약하고 Google Drive에 저장하는 자동화 시스템입니다.

## 🚀 주요 기능

- **자동 뉴스 수집**: 나스닥 RSS 피드에서 최신 뉴스 수집
- **AI 요약**: OpenAI GPT-4를 이용한 뉴스 요약 및 분석
- **번역**: 영문 뉴스를 한국어로 번역
- **자동화**: GitHub Actions를 통한 일일 자동 실행
- **클라우드 저장**: 결과를 Google Drive에 자동 업로드

## 📁 프로젝트 구조

```
nasdaq_news/
├── main.py              # 메인 실행 파일
├── config.py            # 설정 관리
├── fetcher.py           # RSS 뉴스 수집
├── summarizer.py        # AI 요약 기능
├── embedder.py          # 번역 기능
├── index_manager.py     # 데이터 저장 관리
├── search.py            # 검색 기능 (미사용)
├── requirements.txt     # 의존성 패키지
├── .env                 # 환경 변수 (로컬)
└── .github/
    └── workflows/
        └── news.yml     # GitHub Actions 워크플로우
```

## 🔧 설치 및 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd nasdaq_news
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 API 키들을 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key
```

## 📊 수집 대상 뉴스

현재 다음 RSS 피드에서 뉴스를 수집합니다:

- 나스닥 마켓 뉴스
- Apple (AAPL) 관련 뉴스
- Tesla (TSLA) 관련 뉴스
- NVIDIA (NVDA) 관련 뉴스
- Microsoft (MSFT) 관련 뉴스
- 주식 일반 뉴스
- AI 관련 뉴스

## 🤖 자동화 설정 (GitHub Actions)

### Google Cloud 설정

1. **Google Cloud Console 접속**
   - Google Cloud Console에 접속하여 새 프로젝트를 생성합니다.

2. **Google Drive API 활성화**
   - Google Cloud 관리 콘솔에서 `Google Drive API`를 검색하고 활성화합니다.

3. **서비스 계정 생성**
   - [IAM 및 관리자] → [서비스 계정]에서 서비스 계정을 추가합니다.
   - 계정 이름과 설명을 입력하고 [완료] 버튼을 누릅니다.
   - 생성된 서비스 계정에서 [작업] → [키 관리] → [키 추가] → [새 키 만들기]를 클릭합니다.
   - `JSON` 형식으로 키를 생성하고 파일을 다운로드합니다.

### Google Drive 설정

1. **폴더 생성 및 공유**
   - Google Drive에서 파일을 업로드할 폴더를 생성합니다.
   - 폴더를 서비스 계정 이메일과 공유하고 "편집자" 권한을 부여합니다.
   - 폴더 URL에서 `folderId`를 추출합니다.

### GitHub Secrets 등록

Repository의 [Settings] → [Secrets and variables] → [Actions]에서 다음 secrets을 등록하세요:

- `OPENAI_API_KEY`: OpenAI API 키
- `GOOGLE_DRIVE_FOLDER_ID`: Google Drive 폴더 ID
- `GOOGLE_SERVICE_ACCOUNT_CREDENTIALS`: 서비스 계정 JSON 키 (base64 인코딩)

```bash
# JSON 키 파일을 base64로 인코딩
base64 -i service-account-key.json -o encoded_json
```

## 💻 로컬 실행

```bash
python main.py
```

## 📅 자동 실행 스케줄

GitHub Actions는 매일 KST 기준 오전 9시 30분(UTC 0시 30분)에 자동으로 실행됩니다.
수동 실행도 GitHub Actions 탭에서 가능합니다.

## 📝 출력 파일

- `nasdaq_metadata_YYYY-MM-DD.csv`: 수집된 뉴스 데이터
  - ID, 제목, 날짜, 내용(번역), 요약이 포함됩니다.

## 🛠 주요 모듈 설명

- [`main.py`](main.py): 전체 프로세스를 조율하는 메인 스크립트
- [`fetcher.py`](fetcher.py): RSS 피드에서 뉴스를 수집하는 기능
- [`summarizer.py`](summarizer.py): OpenAI GPT-4를 이용한 뉴스 요약
- [`embedder.py`](embedder.py): 영문 뉴스를 한국어로 번역
- [`config.py`](config.py): 파일 경로 및 기본 설정 관리
- [`index_manager.py`](index_manager.py): 데이터를 CSV 파일로 저장

## 🔍 검색 기능 (개발 중)

[`search.py`](search.py)에는 FAISS를 이용한 검색 기능이 구현되어 있지만, 현재는 비활성화 상태입니다.

## 📋 요구사항

주요 의존성 패키지는 [`requirements.txt`](requirements.txt)에서 확인할 수 있습니다:

- `openai`: AI 요약 및 번역
- `beautifulsoup4`: 웹 스크래핑
- `pandas`: 데이터 처리
- `requests`: HTTP 요청
- `python-dotenv`: 환경 변수 관리
- `langchain`: AI 체인 (향후 확장용)

## 📄 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.