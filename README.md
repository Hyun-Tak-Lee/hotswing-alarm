# 웹페이지 HTML 스크래핑 도구

이 프로젝트는 소모임 웹페이지의 HTML을 읽어오는 파이썬 스크래핑 도구입니다.

## 설치 방법

1. 필요한 라이브러리 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

### 기본 사용법

- 아래 URL 로 code 복사 후 code 파일에 할당

https://kauth.kakao.com/oauth/authorize?client_id=299313409980678e0dcfe9e06e1f6bf0&redirect_uri=https://example.com/oauth&response_type=code&scope=profile_nickname,friends,talk_message
    
- web_scraper.py 파일 실행 (파이썬)

## 주의사항

- 과도한 요청은 서버에 부하를 줄 수 있으니 적절한 간격을 두고 사용하세요
- time.sleep(10) == 10초 간격
