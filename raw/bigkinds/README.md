# 빅카인즈에서 받은 엑셀 원본

파일명 권장: `NewsResult_YYYYMMDD-YYYYMMDD.xlsx`  
계획: [`../../docs/계획-빅카인즈-순차다운로드.md`](../../docs/계획-빅카인즈-순차다운로드.md)

| 파일 | 기간 | 건수 | 상태 |
|------|------|------|------|
| `NewsResult_20221029-20221030.xlsx` | 2022-10-29~30 | 4,924 | OK |
| `NewsResult_20221031-20221031.xlsx` | 2022-10-31 | 5,088 | OK |
| `NewsResult_20221101-20221108.xlsx` | 2022-11-01~08 | 18,162 | OK |
| `NewsResult_20221109-20221115.xlsx` | 2022-11-09~15 | 7,409 | OK |
| `NewsResult_20221116-20221130.xlsx` | 2022-11-16~30 | 8,387 | OK |
| `NewsResult_20221201-20221231.xlsx` | 2022-12 | 10,698 | OK |
| `NewsResult_20230101-20230630.xlsx` | 2023 상반 | 14,780 | OK |
| `NewsResult_20230701-20231231.xlsx` | 2023 하반 | 8,798 | OK |
| `NewsResult_2024.xlsx` | 2024 | 13,300 | OK |
| `NewsResult_2025.xlsx` | 2025 | 5,524 | OK |
| `NewsResult_2026.xlsx` | 2026-01-01~08-13 | 2,027 | OK |
| `bigkinds-20260101-20260813.xlsx` | (동일) | 2,027 | **중복** · merge 시 스킵 |

재병합: `python3 scripts/1029_import_bigkinds.py` (기본 경로 = 이 폴더)
