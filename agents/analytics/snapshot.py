#!/usr/bin/env python3
"""متریک امروز: شمار محصول/مقاله، مجموع بازدید مقاله، و آمار GSC (از CSV داخل data/inbox)."""
import csv, pathlib, sys, datetime, os
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import steve
from store.db import conn

steve.BASE = steve.BASE or "https://api.stevemobile.com"
from lib import jalali
day = jalali.iso()
m = {}
P = steve.storefront_products(); A = steve.storefront_articles()
m["products_published"] = len(P); m["articles_published"] = len(A)
m["article_views_total"] = sum(a.get("view_count") or 0 for a in A)
f = ROOT / "data/inbox/gsc_daily.csv"
if f.exists():
    rows = list(csv.DictReader(open(f, encoding="utf8")))[-28:]
    m["gsc_clicks_28d"] = sum(int(r["Clicks"] or 0) for r in rows)
    m["gsc_impressions_28d"] = sum(int(r["Impressions"] or 0) for r in rows)
try:  # خلاصه فروش امن (بعد از deploy بک‌اند)؛ بدون اطلاعات مشتری و هزینه
    d = steve._req("GET", "/backoffice/dashboard/ai-summary", auth=True) or {}
    ds = d.get("daily_sales") or []
    m["orders_30d"] = sum(x.get("order_count") or 0 for x in ds)
    m["revenue_30d_toman"] = sum(x.get("revenue") or 0 for x in ds)  # واحد: تومان (definitions.currency)
    m["revenue_non_catalog_toman"] = d.get("non_catalog_revenue") or 0  # فاکتور دستی بدون محصول کاتالوگ (مثل تعمیر)
    m["revenue_catalog_toman"] = m["revenue_30d_toman"] - m["revenue_non_catalog_toman"]
    m["units_non_catalog"] = d.get("non_catalog_units") or 0
    for st in d.get("cancelled_by_reason") or []:
        m[f"cancelled_reason:{st.get('reason')}"] = st.get("count") or 0
    for i, tp in enumerate((d.get("top_products") or [])[:5]):
        m[f"top{i+1}_units:{tp.get('slug')}"] = tp.get("units_sold") or 0
    for st in d.get("orders_by_status") or []:
        m[f"orders_status:{st.get('status')}"] = st.get("count") or 0
except Exception as e:
    print("ai-summary در دسترس نیست:", str(e)[:60])
c = conn()
for k, v in m.items():
    c.execute("INSERT OR REPLACE INTO metrics(day,key,value) VALUES(?,?,?)", (day, k, v))
c.commit(); print(day, m)
