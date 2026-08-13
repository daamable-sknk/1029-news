#!/usr/bin/env python3
"""
빅카인즈 엑셀(원본) → 1029-articles.json / xlsx 병합

BigKinds 파일은 dimension=A1 + inlineStr 이라 openpyxl이 깨짐 → XML 파싱.

Usage:
  python3 scripts/1029_import_bigkinds.py
  python3 scripts/1029_import_bigkinds.py --dir /path/to/빅카인즈-원본
  python3 scripts/1029_import_bigkinds.py --replace   # 기존 bigkinds 출처만 지우고 재적재
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

BASE = Path(__file__).resolve().parent.parent
DATA_PATH = BASE / "data" / "1029-articles.json"
DEFAULT_DIR = BASE / "raw" / "bigkinds"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def col_key(c: str) -> int:
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def parse_bigkinds_xlsx(path: Path) -> tuple[list[str], list[dict]]:
    with ZipFile(path) as z:
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows_out: list[dict] = []
    for row in root.findall("m:sheetData/m:row", NS):
        cells: dict[str, str] = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r", "")
            m = re.match(r"([A-Z]+)", ref or "")
            if not m:
                continue
            col = m.group(1)
            t = c.find("m:is/m:t", NS)
            v = c.find("m:v", NS)
            if t is not None and t.text is not None:
                cells[col] = t.text
            elif v is not None and v.text is not None:
                cells[col] = v.text
            else:
                cells[col] = ""
        if cells:
            rows_out.append(cells)
    if not rows_out:
        return [], []
    cols = sorted({c for r in rows_out for c in r}, key=col_key)
    header = [rows_out[0].get(c, "") for c in cols]
    data = []
    for r in rows_out[1:]:
        data.append({header[i]: r.get(cols[i], "") for i in range(len(cols))})
    return header, data


def ymd_to_iso(s: str) -> str:
    s = (s or "").strip().replace("-", "")
    if len(s) == 8 and s.isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return s


def canon_url(url: str) -> str:
    return (url or "").strip()


def item_id(news_id: str, url: str, published: str) -> str:
    key = news_id or f"{canon_url(url)}|{published}"
    h = hashlib.md5(key.encode()).hexdigest()[:10]
    return f"bk-{published}-{h}"


def load_db() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {
        "meta": {
            "title": "1029 공공기록 관련 기사 목록",
            "since": "2022-10-29",
            "last_updated": None,
            "total_count": 0,
            "sources": ["google_news", "naver", "bigkinds"],
        },
        "items": [],
    }


def save_db(db: dict) -> None:
    db["meta"]["total_count"] = len(db["items"])
    db["meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sources = sorted({i.get("source") for i in db["items"] if i.get("source")})
    db["meta"]["sources"] = sources
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def row_to_item(row: dict, source_file: str, collected_at: str) -> dict | None:
    title = (row.get("제목") or "").strip()
    url = (row.get("URL") or "").strip()
    news_id = (row.get("뉴스 식별자") or "").strip()
    published = ymd_to_iso(row.get("일자") or "")
    if not title or not published:
        return None
    if published < "2022-10-29":
        return None
    return {
        "id": item_id(news_id, url, published),
        "title": title,
        "published_at": published,
        "author": "",  # 화면·엑셀에는 비움; 원문 기고자는 아래에 보관
        "publisher": (row.get("언론사") or "").strip(),
        "url": url,
        "url_canon": canon_url(url),
        "note": "",
        "collected_at": collected_at,
        "collector": "",
        "source": "bigkinds",
        "query_id": "bigkinds",
        "bigkinds_id": news_id,
        "reporter": (row.get("기고자") or "").strip(),  # 내부 보관 · 표의 기자명은 비움 정책 유지?
        "source_file": source_file,
        "category1": (row.get("통합 분류1") or "").strip(),
    }


def existing_keys(db: dict) -> set[str]:
    keys = set()
    for it in db.get("items", []):
        if it.get("bigkinds_id"):
            keys.add(f"bkid:{it['bigkinds_id']}")
        if it.get("url_canon"):
            keys.add(f"url:{it['url_canon']}")
        # title+date soft key
        keys.add(f"td:{it.get('published_at')}|{it.get('title')}")
    return keys


def import_file(path: Path, db: dict, keys: set[str], collected_at: str) -> dict:
    print(f"  parsing {path.name} …", flush=True)
    header, data = parse_bigkinds_xlsx(path)
    if "제목" not in header:
        return {"file": path.name, "error": "no 제목 column", "rows": 0, "added": 0}
    added = 0
    skipped = 0
    for row in data:
        it = row_to_item(row, path.name, collected_at)
        if not it:
            skipped += 1
            continue
        k_id = f"bkid:{it['bigkinds_id']}" if it["bigkinds_id"] else None
        k_url = f"url:{it['url_canon']}" if it["url_canon"] else None
        k_td = f"td:{it['published_at']}|{it['title']}"
        if (k_id and k_id in keys) or (k_url and k_url in keys) or k_td in keys:
            skipped += 1
            continue
        # 빅카인즈 기고자 → 기자명. 작성자(기입자)·비고는 비움
        it["author"] = it.get("reporter") or ""
        it["collector"] = ""
        it["note"] = ""
        db["items"].append(it)
        if k_id:
            keys.add(k_id)
        if k_url:
            keys.add(k_url)
        keys.add(k_td)
        added += 1
    return {
        "file": path.name,
        "rows": len(data),
        "added": added,
        "skipped": skipped,
        "date_min": min((r.get("일자") or "99999999") for r in data) if data else None,
        "date_max": max((r.get("일자") or "") for r in data) if data else None,
    }


def export_xlsx(db: dict) -> None:
    # reuse collect export if available
    sys.path.insert(0, str(Path(__file__).parent))
    import importlib.util

    spec = importlib.util.spec_from_file_location("collect", Path(__file__).parent / "1029_collect.py")
    collect = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(collect)
    collect.export_xlsx(db)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    ap.add_argument(
        "--replace",
        action="store_true",
        help="remove existing source=bigkinds items before import",
    )
    ap.add_argument("--skip-duplicate-2026", action="store_true", default=True)
    args = ap.parse_args()

    files = sorted(args.dir.glob("*.xlsx"), key=lambda p: p.name)
    # Prefer NewsResult_2026.xlsx; skip renamed duplicate
    if args.skip_duplicate_2026:
        names = {f.name for f in files}
        if "NewsResult_2026.xlsx" in names and "bigkinds-20260101-20260813.xlsx" in names:
            files = [f for f in files if f.name != "bigkinds-20260101-20260813.xlsx"]
            print("skip duplicate: bigkinds-20260101-20260813.xlsx (keep NewsResult_2026.xlsx)")

    db = load_db()
    if args.replace:
        before = len(db["items"])
        db["items"] = [i for i in db["items"] if i.get("source") != "bigkinds"]
        print(f"removed bigkinds items: {before - len(db['items'])}")

    keys = existing_keys(db)
    collected_at = today()
    reports = []
    print(f"importing {len(files)} files into {DATA_PATH}")
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}]")
        rep = import_file(f, db, keys, collected_at)
        reports.append(rep)
        print(f"  → rows={rep.get('rows')} added={rep.get('added')} skipped={rep.get('skipped')}")

    db["items"].sort(key=lambda x: x.get("published_at") or "", reverse=True)
    save_db(db)
    export_xlsx(db)

    log_path = args.dir.parent / "빅카인즈-병합로그.json"
    log_path.write_text(
        json.dumps(
            {
                "merged_at": collected_at,
                "total_items": len(db["items"]),
                "files": reports,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"done total={len(db['items'])} log={log_path}")


if __name__ == "__main__":
    main()
