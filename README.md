
# GitHub Actions를 이용한 Google Drive 배포 자동화

이 문서에서는 GitHub Actions와 Google Cloud를 사용하여 Google Drive에 개발 결과물을 배포하는 방법에 대해 설명합니다.

## 사용 라이브러리

- `google-drive-upload-git-action`: GitHub Actions에서 Google Drive로 파일을 업로드하는 기능을 제공하는 라이브러리입니다.

## Google Cloud 설정

1. **Google Cloud Console 접속**Google Cloud Console에 접속하여 새 프로젝트를 생성하고 해당 프로젝트로 전환합니다.
2. **Google Drive API 활성화**Google Cloud 관리 콘솔에서 `Google Drive API`를 검색하고 선택한 후, API를 활성화합니다.
3. **서비스 계정 생성**

   - [IAM 및 관리자] → [서비스 계정]에서 서비스 계정을 추가합니다.
   - 계정 이름과 설명을 입력하고 나머지 설정을 무시한 후, [완료] 버튼을 누릅니다.
   - 생성된 서비스 계정에서 [작업] 메뉴를 열고 [키 관리]를 선택한 후, [키 추가] → [새 키 만들기]를 클릭합니다.
   - `JSON` 형식으로 키를 생성하고 비공개 키 파일을 로컬에 저장합니다. 이 파일은 안전하게 보관해야 합니다.

## Google Drive 설정

1. **Google Drive 폴더 생성**Google Cloud 관리 콘솔과 동일한 계정으로 Google Drive에 접속하여 파일을 업로드할 폴더를 생성합니다.
2. **서비스 계정 권한 설정**

   - Google Drive 폴더에서 [액세스 관리] → [사용자 및 그룹 추가]를 선택합니다.
   - 서비스 계정 이메일(형식: `google-drive-access@xxxxx-xxxxx-xxxxx.iam.gserviceaccount.com`)을 추가하고, 권한을 "편집자"로 설정한 후 [공유] 버튼을 클릭합니다.
3. **폴더 ID 추출**

   - 공유된 폴더의 URL에서 `folderId`를 추출하여 기록해 둡니다. (URL 형식: `drive.google.com/drive/folders/<folderId>`)

## GitHub Actions 설정

1. **GitHub Secrets 등록**

   - GitHub 저장소의 [Settings] → [Secrets and variables] → [Actions] 메뉴에서 `New repository secret`을 클릭하여 Google Drive 폴더 ID를 `GOOGLE_DRIVE_FOLDER_ID`라는 이름으로 등록합니다.
   - 또한, Google Cloud 서비스 계정의 JSON 키를 base64로 인코딩한 후 `GOOGLE_SERVICE_ACCOUNT_CREDENTIALS`라는 이름으로 등록합니다.

   ```bash
   $ base64 -i xxxxxxxxx-xxxx-xxxxxx-xxxxxxxxxxx.json -o encoded_json
   ```
