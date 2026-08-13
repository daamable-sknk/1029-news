# 1029 언론 기사 목록 — 작업 노트

공개: https://daamable-sknk.github.io/1029-news/  
계획: [계획-이태원-기사스크랩.md](계획-이태원-기사스크랩.md) · [계획-빅카인즈-순차다운로드.md](계획-빅카인즈-순차다운로드.md)

## 구성

| 경로 | 역할 |
|------|------|
| [`../index.html`](../index.html) | 목록 페이지 |
| [`../data/1029-articles.json`](../data/1029-articles.json) | 수집 데이터 |
| [`../scripts/1029_queries.yaml`](../scripts/1029_queries.yaml) | 검색식 |
| [`../scripts/1029_collect.py`](../scripts/1029_collect.py) | Google · 네이버 |
| [`../scripts/1029_import_bigkinds.py`](../scripts/1029_import_bigkinds.py) | 빅카인즈 원본 병합 |
| [`../raw/bigkinds/`](../raw/bigkinds/) | 빅카인즈 엑셀 원본 |
| `.github/workflows/collect.yml` | 일일 수집 |

## GitHub Secrets

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
