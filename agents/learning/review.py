#!/usr/bin/env python3
"""شواهد هفتگی برای ایجنت یادگیری (JSON/متن). فقط می‌خواند؛ تفسیر با Claude طبق skills/learning.md"""
import csv, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from store.db import conn
from lib import jalali

c = conn()
out = {"today": jalali.iso()}
days = sorted({r[0] for r in c.execute("SELECT DISTINCT day FROM metrics")})[-2:]
snap = {d: {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM metrics WHERE day=?", (d,))} for d in days}
out["metrics_last_two_snapshots"] = snap
f = ROOT / "data/inbox/gsc_daily.csv"
if f.exists():
    rows = list(csv.DictReader(open(f, encoding="utf8")))
    def agg(rs): return {"clicks": sum(int(r["Clicks"] or 0) for r in rs), "impressions": sum(int(r["Impressions"] or 0) for r in rs)}
    out["gsc"] = {"last_14d": agg(rows[-14:]), "prev_14d": agg(rows[-28:-14]), "last_date_in_file": rows[-1]["Date"]}
    out["gsc"]["warning"] = "نمونه کوچک: اختلاف زیر ~۳۰ کلیک را نتیجه‌گیری نکن" if out["gsc"]["last_14d"]["clicks"] < 30 else ""
out["proposal_stats"] = [dict(r) for r in c.execute("SELECT kind,status,count(*) n FROM proposals GROUP BY kind,status")]
out["experiments_due"] = [dict(r) for r in c.execute("SELECT * FROM experiments WHERE status='open' AND due_day<=?", (jalali.iso(),))]
out["experiments_open"] = [dict(r) for r in c.execute("SELECT id,what,due_day FROM experiments WHERE status='open'")]
out["recent_learnings"] = [dict(r) for r in c.execute("SELECT day,topic,insight FROM learnings ORDER BY id DESC LIMIT 8")]
ig = ROOT / "data/inbox/ig_insights.csv"
out["instagram_insights"] = "فایل data/inbox/ig_insights.csv موجود است" if ig.exists() else "ندارم (ستون‌ها: date,post,reach,saves,shares,link_clicks — خروجی دستی Insights)"
print(json.dumps(out, ensure_ascii=False, indent=1))
