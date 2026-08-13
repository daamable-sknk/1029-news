# 1029-news

1029 이태원 참사 · **공공기록 관련 언론 기사** 수집·목록.

| | |
|--|--|
| **웹 (공개 주소)** | https://meta-archives.xyz/1029.html |
| **데이터·이 저장소 Pages** | https://daamable-sknk.github.io/1029-news/ |
| **저장소** | https://github.com/daamable-sknk/1029-news |
| **연구 맥락** | `docs/daam/1029-itaewon` (계획·조사는 그쪽, **스크랩 작업은 여기**) |

공개 목록 URL은 **meta-archives**에 두고, JSON·엑셀·수집 스크립트만 이 저장소에 둡니다.

## 구성

```
index.html                 # 목록 페이지
data/1029-articles.json    # 병합 데이터 (~9.6만 건)
data/1029-articles.xlsx    # 엑셀 다운로드
scripts/1029_collect.py    # Google News · 네이버
scripts/1029_import_bigkinds.py
scripts/1029_queries.yaml
seed/                      # 황나은 시드 엑셀
raw/bigkinds/              # 빅카인즈 원본 xlsx
docs/                      # 수집 계획
```

## 로컬

```bash
cd /Users/skunk/docs/daam/1029-news
python3 -m http.server 8767   # http://127.0.0.1:8767/

# 신규 수집 (네이버는 환경변수 필요)
export NAVER_CLIENT_ID=...
export NAVER_CLIENT_SECRET=...
python3 scripts/1029_collect.py --source google
python3 scripts/1029_collect.py --source all

# 빅카인즈 원본 재병합
python3 scripts/1029_import_bigkinds.py
```

의존: `pip install feedparser requests pyyaml openpyxl`

## GitHub Actions

`.github/workflows/collect.yml` — 매일 10:00 KST 수집 후 `data/` 커밋.

Secrets: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` (없으면 Google만).

## 칼럼

`기사제목 · 발행날짜 · 기자명 · 발행처 · url · 비고 · 작성일 · 작성자`  
자동화는 **비고·작성자(기입자) 비움**. 담당자가 엑셀에서 채움.
