# merge_files.py

import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from io import BytesIO
import json
from google.oauth2.service_account import Credentials

# 구글 드라이브 API 인증 설정
def authenticate_google_drive():
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS")  # JSON contents from GitHub Secrets
    creds_info = json.loads(creds_json)  # Convert string to JSON
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=creds)
    return service

# 구글 드라이브에서 파일 다운로드
def download_file_from_drive(file_id, destination_path):
    service = authenticate_google_drive()
    request = service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    with open(destination_path, 'wb') as f:
        f.write(fh.read())

# 구글 드라이브에서 파일 업로드 (덮어쓰기)
def upload_file_to_drive(file_id, file_path):
    service = authenticate_google_drive()
    media = MediaFileUpload(file_path, resumable=True)
    request = service.files().update(fileId=file_id, media_body=media)
    response = request.execute()
    print(f"✅ Google Drive에 파일 업로드 완료: {response['name']}")

# 메타데이터와 인덱스 파일 병합
def merge_files_from_drive():
    # Google Drive에서 파일 다운로드
    metadata_file_id = os.getenv("GOOGLE_DRIVE_METADATA_FILE_ID")  # 환경변수에서 파일 ID 가져오기
    index_file_id = os.getenv("GOOGLE_DRIVE_INDEX_FILE_ID")

    metadata_local_path = 'nasdaq_metadata.csv'  # 로컬에서 생성된 파일
    index_local_path = 'nasdaq_index.faiss'

    # Google Drive에서 파일 다운로드하여 임시로 다른 이름으로 저장
    download_file_from_drive(metadata_file_id, 'nasdaq_metadata_drive.csv')  # Google Drive에서 받은 메타데이터
    download_file_from_drive(index_file_id, 'nasdaq_index_drive.faiss')

    # 기존 메타데이터 파일을 읽고, 새로 생성된 메타데이터를 병합
    existing_df = pd.read_csv('nasdaq_metadata_drive.csv')  # Google Drive에서 다운로드한 데이터
    new_df = pd.read_csv(metadata_local_path)  # 로컬에서 생성된 데이터
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    # 병합된 데이터를 다시 기존 이름으로 저장 (로컬에서 덮어쓰지 않게, 병합된 데이터를 새로 저장)
    combined_df.to_csv('nasdaq_metadata_combined.csv', index=False)  # 병합된 파일로 저장

    # 병합된 데이터와 인덱스를 다시 구글 드라이브에 업로드
    upload_file_to_drive(metadata_file_id, 'nasdaq_metadata_combined.csv')  # Google Drive에 덮어쓰기
    print("📑 메타데이터 파일 병합 완료")
