#!/usr/bin/env python3
"""ورودی ایجنت بازاریابی → data/reports/marketing_context.json
کاتالوگ (واقعی)، تخفیف‌های فعال، فرصت‌های سئو/GSC، متریک‌ها و خلاصه فروش (اگر endpoint امن آماده باشد)."""
import csv, json, pathlib, re, sys, collections
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import steve
from store.db import conn

steve.BASE = steve.BASE or "https://api.stevemobile.com"
ctx = {}
P = steve.storefront_products()
buckets = collections.Counter()
for p in P:
    n = p["name"]
    if re.search(r"گیگابایت|\bGB\b", n + p.get("en_title", "")) and re.search(r"آیفون|iPhone|گوشی", n):
        buckets["گوشی (آیفون)"] += 1
        continue
    k = next((w for w in ["قاب", "گارد", "کاور", "محافظ لنز", "گلس", "هدفون", "هندزفری", "کابل", "شارژر", "آداپتور", "پاوربانک", "اسپیکر", "میکروفون", "ساعت", "گوشی موبایل"] if w in n), "سایر")
    buckets[k] += 1
instock = sum(1 for p in P if any((v.get("quantity") or 0) > 0 for v in p.get("variant") or []))
ctx["catalog"] = {"total": len(P), "in_stock": instock, "by_type": dict(buckets.most_common())}
try:
    d = steve._req("GET", "/product/storefront/with-auto-discount", {"page_number": 1, "page_size": 50}) or {}
    ctx["active_auto_discounts"] = [x.get("name") for x in (d.get("products") or [])][:20]
except Exception as e:
    ctx["active_auto_discounts"] = f"ERR {e}"
f = ROOT / "data/inbox/gsc_tab2.csv"
if f.exists():
    ctx["gsc_top_queries"] = list(csv.DictReader(open(f, encoding="utf8")))[:15]
ctx["metrics"] = [dict(r) for r in conn().execute("SELECT day,key,value FROM metrics ORDER BY day DESC LIMIT 12")]
try:  # endpoint امن خلاصه فروش (بعد از پیاده‌سازی بک‌اند)
    ctx["sales_summary"] = steve._req("GET", "/backoffice/dashboard/ai-summary", auth=True)
except Exception as e:
    ctx["sales_summary"] = f"موجود نیست ({str(e)[:40]}) — داده فروش واقعی ندارم؛ پیشنهادها بدون آن حدسی‌اند"
(ROOT / "data/reports/marketing_context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=1))
print(json.dumps(ctx["catalog"], ensure_ascii=False), ctx["sales_summary"] if isinstance(ctx["sales_summary"], str) else "sales ok")
