#!/usr/bin/env python3
"""دانلود دوباره شیت Search Console (لینک اشتراکی که کاربر داد) → data/inbox. فقط اگر شیت به‌روز شده باشد جدید است."""
import pathlib, urllib.request
SHEET = "1ffmsbzpWcEgHWY3L3SniHYnjLmi5vajJ36gB1XTciJs"
ROOT = pathlib.Path(__file__).resolve().parent.parent
import json, sys
imp = ROOT / "data/inbox/gsc_import.json"
if imp.exists():  # export دستی تازه (کمتر از ۷ روز) را با شیت قدیمی بازنویسی نکن
    import datetime
    if (datetime.datetime.now() - datetime.datetime.fromtimestamp(imp.stat().st_mtime)).days < 7:
        print("export دستی GSC تازه است؛ شیت دانلود نشد"); sys.exit(0)
for name, gid in (("gsc_daily.csv", ""), ("gsc_tab2.csv", "1591478643")):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET}/export?format=csv" + (f"&gid={gid}" if gid else "")
    data = urllib.request.urlopen(url, timeout=30).read()
    (ROOT / "data/inbox" / name).write_bytes(data); print(name, len(data.splitlines()), "ردیف")
