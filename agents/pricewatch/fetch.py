#!/usr/bin/env python3
"""قیمت رقبا فقط از لینک‌هایی که خودتان داده‌اید (data/inbox/competitor_links.csv: slug,url,note) + ورودی دستی (competitor_prices_manual.csv).
قوانین رعایت شرایط: فقط صفحه محصول ترب (/p/…؛ robots آن فقط /search/ را بسته)، بدون جستجو/API داخلی، با فاصله ۵ ثانیه، UA مشخص، سقف ۵۰ لینک.
قیمت ترب به ریال است → تقسیم بر ۱۰ = تومان (واحد سایت ما)."""
import csv, json, pathlib, re, sys, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from store.db import conn
from lib import jalali

UA = "Mozilla/5.0 (compatible; SteveMobilePriceCheck/1.0; +https://stevemobile.com)"
day, c = jalali.iso(), conn()
from lib import steve
api = (steve._req("GET", "/product/competitor-links", auth=True) or {}).get("products") or []
links = [{"slug": x["slug"], "url": x.get("torob_url"), "id": x["id"]} for x in api]
f = ROOT / "data/inbox/competitor_links.csv"
if not links and f.exists():
    links = list(csv.DictReader(open(f, encoding="utf8")))
links = links[:50]
ok = 0
for r in links:
    url = (r.get("url") or "").strip()
    if not re.match(r"^https://torob\.com/p/[0-9a-f-]{36}", url):
        print("رد شد (فقط لینک صفحه محصول ترب):", url[:50]); continue
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode("utf8", "ignore")
        low = re.search(r'lowPrice"\s*:\s*"?(\d+)', html); high = re.search(r'highPrice"\s*:\s*"?(\d+)', html); n = re.search(r'offerCount"\s*:\s*"?(\d+)', html)
        if not low: print("قیمت پیدا نشد:", r["slug"]); continue
        c.execute("INSERT OR REPLACE INTO competitor_prices VALUES(?,?,?,?,?,?)",
                  (day, r["slug"], "torob", int(low.group(1)) / 10, int(high.group(1)) / 10 if high else None, int(n.group(1)) if n else None))
        ok += 1
        if r.get("id"):  # فقط ۴ فیلد رقیب؛ قیمت فروش دست نمی‌خورد
            steve._req("PATCH", f"/product/{r['id']}/competitor-price", auth=True, body={
                "min_price": int(low.group(1)) // 10, "max_price": int(high.group(1)) // 10 if high else None,
                "offers_count": int(n.group(1)) if n else None, "checked_at": day})
    except Exception as e:
        print("خطا", r["slug"], str(e)[:60])
    time.sleep(5)
m = ROOT / "data/inbox/competitor_prices_manual.csv"  # slug,competitor,price_toman
if m.exists():
    for r in csv.DictReader(open(m, encoding="utf8")):
        c.execute("INSERT OR REPLACE INTO competitor_prices VALUES(?,?,?,?,?,?)", (day, r["slug"], r["competitor"], float(r["price_toman"]), float(r["price_toman"]), 1)); ok += 1
c.commit(); print(ok, "قیمت ذخیره شد")
