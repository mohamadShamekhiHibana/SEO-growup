#!/usr/bin/env python3
"""پیشنهاد لینک داخلی برای مقاله‌های منتشرشده (فقط خواندنی).
ورودی: data/reports/articles_links.json (لینک‌های فعلی) + products_full.json. مقاله‌ها را تغییر نمی‌دهد.
خروجی: data/reports/internal_links.md"""
import json, re, sys, pathlib, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib import jalali

SITE = "https://stevemobile.com"
# موضوع مقاله → صفحه خدمات/دسته + کلیدواژه‌های نام محصول
RULES = [
    (r"شارژر|کابل|پاوربانک|باتری", "/phone-repair", ["شارژر", "کابل", "پاوربانک", "آداپتور"]),
    (r"تاچ|ال ?سی ?دی|LCD|صفحه|تعمیر|هنگ|داغ", "/phone-repair", ["گلس", "محافظ صفحه"]),
    (r"دست ?دوم|ریپک|رجیستر|گارانتی|خرید گوشی|دانش‌?آموز", "/phone-sales", []),
    (r"قاب|کاور|کیف", None, ["قاب", "کاور"]),
    (r"لنز|دوربین", None, ["محافظ لنز", "لنز"]),
    (r"هدفون|هندزفری|ایرپاد|بلوتوث", None, ["هدفون", "هندزفری", "ایرپاد"]),
    (r"آیفون|iOS|ios", None, ["آیفون"]),
]
STOP = set("و در به از که با را این برای یک تا است چه چطور گوشی + ؛ ، ? ؟ - های ها راهنمای راهنما انتخاب خرید علت روش نکته چیست بهترین واقعی قطعی امروز کامل".split())


def tokens(s):
    return {w for w in re.split(r"[\s\-_،؛:؟?!+()«»\"']+", s or "") if len(w) > 2 and w not in STOP}


def main():
    arts = json.loads((ROOT / "data/reports/articles_links.json").read_text())
    prods = json.loads((ROOT / "data/reports/products_full.json").read_text())
    live = [p for p in prods if p.get("is_published", True)]
    out = [f"# پیشنهاد لینک داخلی مقاله‌ها — {jalali.human()}", "",
           f"{len(arts)} مقاله منتشرشده؛ {sum(a['product_links'] == 0 for a in arts)} مقاله هیچ لینکی به محصول ندارند و "
           f"{sum(a['blog_links'] == 0 for a in arts)} مقاله به مقاله دیگری لینک نداده‌اند.",
           "روش: در هر مقاله ۲–۴ لینک با anchor طبیعی داخل متن (نه فهرست انتهایی). هیچ مقاله‌ای تغییر نکرده؛ اعمال فقط با تأیید.", ""]
    for a in sorted(arts, key=lambda x: (x["product_links"] + x["blog_links"], -(x["views"] or 0))):
        if a["product_links"] >= 2 and a["blog_links"] >= 1: continue
        title = a["title"] or a["slug"]
        sugg = []
        for pat, page, kws in RULES:
            if not re.search(pat, title, re.I): continue
            if page and not any(page in s for s in sugg): sugg.append(f"صفحه خدمات: {SITE}{page}")
            hits = [p for p in live if any(k in (p.get("name") or "") for k in kws)]
            ttl = tokens(title)
            hits.sort(key=lambda p: -len(ttl & tokens(p.get("name"))))
            for p in hits[:2]:
                line = f"محصول: {p['name'].strip()} — {SITE}/product/{p['slug']}"
                if line not in sugg: sugg.append(line)
        ttl = tokens(title)
        rel = sorted((b for b in arts if b["slug"] != a["slug"]), key=lambda b: -len(ttl & tokens(b["title"])))[:2]
        sugg += [f"مقاله مرتبط: {b['title'].strip()} — {SITE}/blog/{b['slug']}" for b in rel if ttl & tokens(b["title"])]
        if not sugg: continue
        out += [f"## {title.strip()}", f"`{a['slug']}` · بازدید {a['views'] or 0} · لینک محصول {a['product_links']} · لینک مقاله {a['blog_links']}",
                *[f"- {s}" for s in sugg[:5]], ""]
    (ROOT / "data/reports/internal_links.md").write_text("\n".join(out))
    print("\n".join(out[:3]))
    print("sections:", sum(1 for l in out if l.startswith("## ")))


if __name__ == "__main__":
    main()
