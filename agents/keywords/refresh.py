#!/usr/bin/env python3
"""به‌روزرسانی خودکار data/reports/keyword_plan.md:
۱) GSC تازه (در صورت امکان)  ۲) نگاشت کوئری‌ها به مقاله‌ها (شامل draft)/محصولات  ۳) افزودن ایده‌های جدید برای کوئری‌های بی‌صفحه
۴) علامت ✅ برای ایده‌های پوشش‌داده‌شده. بخش دستی فایل دست‌نخورده می‌ماند؛ فقط بلوک AUTO بازنویسی می‌شود."""
import csv, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import steve, jalali

try:
    subprocess.run([sys.executable, str(ROOT / "scripts/fetch_gsc.py")], check=True, capture_output=True, timeout=60)
except Exception as e:
    print("GSC تازه گرفته نشد، از فایل قبلی استفاده می‌شود:", str(e)[:50])

steve.BASE = steve.BASE or "https://api.stevemobile.com"
STOP = set("و در به از برای با که این را است یا یک خرید قیمت مدل نرمال".split())
norm = lambda s: re.sub(r"[‌ـ]", " ", s.replace("ي", "ی").replace("ك", "ک")).lower()
toks = lambda s: {t for t in re.findall(r"[\w]+", norm(s)) if t not in STOP and len(t) > 1}

pages = []
try:  # مقاله‌ها با draft (توکن بک‌آفیس)
    p = 1
    while True:
        d = steve._req("GET", "/article", {"page_number": p, "page_size": 50}, auth=True)
        pages += [("article", a["slug"], a["title"] + " " + " ".join(a.get("tags") or []), a["is_published"]) for a in d["articles"]]
        if len(pages) >= d["pagination"]["total"] or not d["articles"]: break
        p += 1
except Exception:
    pages += [("article", a["slug"], a["title"] + " " + " ".join(a.get("tags") or []), True) for a in steve.storefront_articles()]
pages += [("product", x["slug"], x["name"] + " " + (x.get("en_title") or ""), True) for x in steve.storefront_products()]
index = [(k, s, toks(t), pub) for k, s, t, pub in pages]


def match(text):
    q = toks(text)
    best = (0, None)
    for k, s, tk, pub in index:
        if len(q) < 2: continue  # کوئری یک‌کلمه‌ای نگاشت‌پذیر نیست
        sc = len(q & tk) / len(q)
        if sc > best[0]: best = (sc, (k, s, pub))
    return best

rows = []
f = ROOT / "data/inbox/gsc_tab2.csv"
for r in csv.DictReader(open(f, encoding="utf8")):
    q = r["Top queries"]; imp = int(r["Impressions"] or 0); pos = float(r["Position"] or 0)
    if re.search(r"استیو|stevemobile|steven", norm(q)): act, tgt = "برند (بدون اقدام)", ""
    else:
        sc, m = match(q)
        if sc >= 0.6:
            tgt = f"{m[0]}:{m[1]}" + ("" if m[2] else " (draft)")
            act = "بهبود صفحه موجود (جایگاه %.0f)" % pos if pos > 8 else "حفظ/بهبود CTR"
        else: tgt, act = "—", "ایده جدید"
    rows.append((q, imp, pos, tgt, act))
rows.sort(key=lambda x: -x[1])
auto = ["<!-- AUTO:START -->", f"## نگاشت خودکار کوئری‌های GSC (به‌روز: {jalali.human()})",
        "| کوئری | نمایش | جایگاه | صفحه | اقدام |", "|---|---|---|---|---|"]
auto += [f"| {q} | {i} | {p:.0f} | {t} | {a} |" for q, i, p, t, a in rows[:30]]
auto.append("<!-- AUTO:END -->")

path = ROOT / "data/reports/keyword_plan.md"
txt = path.read_text(encoding="utf8")
txt = re.sub(r"\n?<!-- AUTO:START -->.*?<!-- AUTO:END -->\n?", "\n", txt, flags=re.S).rstrip() + "\n\n" + "\n".join(auto) + "\n"

# ایده‌های جدید زیر «فرصت‌های محتوایی» + علامت ✅
head = "## فرصت‌های محتوایی جدید"
if head in txt:
    pre, rest = txt.split(head, 1); body, tail = (rest.split("\n## ", 1) + [""])[:2] if "\n## " in rest else (rest, "")
    lines = body.split("\n"); out = []; seen = []
    for ln in lines:
        m = re.match(r"^([۰-۹0-9]+[.)])\s*(.+)$", ln.strip())
        if m:
            seen.append(norm(m.group(2)))
            if "✅" not in ln:
                sc, mm = match(re.sub(r"[«»]", "", m.group(2)))
                if sc >= 0.75 and mm: ln = ln.rstrip() + f" ✅ موجود: {mm[1]}"
        out.append(ln)
    n = len(seen)
    for q, i, p, t, a in rows:
        if a == "ایده جدید" and i >= 1 and not any(norm(q) in s for s in seen):
            n += 1; out.append(f"{n}. «{q}» — ایده خودکار از GSC ({i} نمایش، جایگاه {p:.0f}) ({jalali.iso()})"); seen.append(norm(q))
    txt = pre + head + "\n".join(out) + ("\n## " + tail if tail else "")
path.write_text(txt, encoding="utf8")
print("keyword_plan.md به‌روز شد؛ ایده جدید:", sum(1 for r in rows if r[4] == "ایده جدید"))
