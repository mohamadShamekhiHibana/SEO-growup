#!/usr/bin/env python3
"""گزارش موقعیت قیمتی ما در برابر رقبا → data/reports/pricewatch/<شمسی>.md (فقط پیشنهاد؛ هیچ قیمتی تغییر نمی‌کند)."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import steve, jalali
from store.db import conn

steve.BASE = steve.BASE or "https://api.stevemobile.com"
c, day = conn(), jalali.iso()
rows = c.execute("SELECT slug,source,low,high,offers FROM competitor_prices WHERE day=(SELECT max(day) FROM competitor_prices)").fetchall()
if not rows:
    print("داده رقبا نیست؛ لینک‌ها را در data/inbox/competitor_links.csv بگذارید"); sys.exit(0)
out = [f"# گزارش قیمت رقبا — {jalali.human()}", "قیمت‌ها تومان. فقط پیشنهاد؛ تصمیم قیمت با مالک. مبنای ما: ارزان‌ترین واریانت موجود (در غیر این صورت ارزان‌ترین).", "",
       "| محصول | قیمت ما | کمترین رقیب | بیشترین | تعداد فروشنده | اختلاف با کمترین | وضعیت |", "|---|---|---|---|---|---|---|"]
for slug, src, low, high, offers in rows:
    try:
        p = steve.product_by_slug(slug); p = p.get("product", p)
        vs = p["variants"]; av = [v["price"] for v in vs if (v.get("quantity") or 0) > 0]
        mine, stock = (min(av), "موجود") if av else (min(v["price"] for v in vs), "ناموجود")
    except Exception as e:
        out.append(f"| {slug} | ؟ | — | — | — | — | محصول پیدا نشد |"); continue
    d = (mine - low) / low * 100
    st = "گران‌تر (بالای ۱۰٪)" if d > 10 else "کمی گران‌تر" if d > 3 else "هم‌قیمت" if d >= -3 else "ارزان‌تر (فرصت افزایش یا فروش بیشتر)"
    out.append(f"| {p['name'].strip()[:40]} ({src}) | {mine:,.0f} ({stock}) | {low:,.0f} | {high:,.0f} | {offers or '—'} | {d:+.0f}٪ | {st} |")
out += ["", "**هشدارها:** ۱) مطمئن شوید لینک رقیب دقیقاً همان مدل/رنگ/ظرفیت/نوع (فعال یا نات‌اکتیو) است. ۲) کمترین قیمت ممکن است از فروشنده‌ی ناشناس یا ناموجود باشد. ۳) هزینه خرید ما را نمی‌دانم؛ قبل از هر کاهش قیمت حاشیه سود را چک کنید."]
f = ROOT / f"data/reports/pricewatch/{day}.md"; f.write_text("\n".join(out), encoding="utf8"); print(f.name, len(rows), "ردیف")
