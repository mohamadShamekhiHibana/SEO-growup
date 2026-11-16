#!/usr/bin/env python3
"""پیشنهاد اصلاح سئوی همه محصولات (فقط خواندنی؛ چیزی در API نوشته نمی‌شود).
- برند «متفرقه» → برند واقعی از specifications (تطبیق با برندهای موجود)
- alt برای هر عکس گالری از نام واقعی محصول
- علامت‌گذاری نام‌های بلند (>۶۰) برای seo_title دستی
خروجی: data/reports/product_seo_fixes.json + product_seo_fixes.md"""
import json, re, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib import steve, jalali

CACHE = ROOT / "data/reports/products_full.json"
SUSPECT = re.compile(r"protector|film|glass|case$|rgb|^\d|redmi|iphone|galaxy", re.I)
EMPTY = {"", "-", "—", "ندارد", "متفرقه", "none", "null"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main(refresh=False):
    if refresh or not CACHE.exists():
        prods = [steve.product_by_slug(p["slug"]).get("product", {}) for p in steve.storefront_products()]
        CACHE.write_text(json.dumps(prods, ensure_ascii=False))
    prods = json.loads(CACHE.read_text())
    brands = {}
    for f in prods:
        b = f.get("brand") or {}
        if b.get("name") and b["name"] != "متفرقه": brands[norm(b["name"])] = b
    fixes, stats = [], collections.Counter()
    for f in prods:
        name = re.sub(r"\s+", " ", (f.get("name") or "").strip())
        item = {"slug": f["slug"], "name": name, "changes": {}}
        cur = (f.get("brand") or {}).get("name")
        spec = next((s.get("value", "").strip() for s in f.get("specifications") or [] if s.get("key") == "brand"), "")
        if cur in (None, "متفرقه") and spec.lower() not in EMPTY:
            match = brands.get(norm(spec)) or next((b for k, b in brands.items() if len(norm(spec)) >= 4 and (norm(spec) in k or k in norm(spec))), None)
            if not match and (len(norm(spec)) <= 3 or SUSPECT.search(spec)):
                item["changes"]["brand_review"] = {"spec_value": spec, "note": "مقدار برند در مشخصات معتبر به نظر نمی‌رسد؛ بررسی دستی"}
                stats["brand_review"] += 1
                spec = ""
        if cur in (None, "متفرقه") and spec.lower() not in EMPTY:
            item["changes"]["brand"] = {"from": cur, "to": match["name"] if match else spec, "brand_id": match["id"] if match else None,
                                        "note": "برند موجود" if match else "برند جدید باید در بک‌آفیس ساخته شود"}
            stats["brand_existing" if match else "brand_new"] += 1
        elif cur and cur != cur.strip():
            item["changes"]["brand_name_whitespace"] = {"from": cur, "to": cur.strip()}
            stats["brand_whitespace"] += 1
        alts = []
        for i, g in enumerate(f.get("gallery") or []):
            if not (g.get("alt") or "").strip():
                alts.append({"media_id": g.get("media_id"), "alt": name if i == 0 else f"{name} - تصویر {i + 1}"})
        if alts: item["changes"]["gallery_alt"] = alts; stats["products_alt"] += 1; stats["images_alt"] += len(alts)
        if len(name) > 60: item["changes"]["long_name"] = len(name); stats["long_name"] += 1
        if item["changes"]: fixes.append(item)

    (ROOT / "data/reports/product_seo_fixes.json").write_text(json.dumps(fixes, ensure_ascii=False, indent=1))
    new_brands = collections.Counter(x["changes"]["brand"]["to"] for x in fixes if "brand" in x["changes"] and not x["changes"]["brand"]["brand_id"])
    ws = sorted({x["changes"]["brand_name_whitespace"]["from"] for x in fixes if "brand_name_whitespace" in x["changes"]})
    md = [f"# پیشنهاد اصلاح سئوی محصولات — {jalali.human()}", "",
          f"- محصولات بررسی‌شده: {len(prods)}",
          f"- برند «متفرقه» با مقدار مشکوک در مشخصات (بررسی دستی): {stats['brand_review']}",
          f"- برند «متفرقه» قابل اصلاح: {stats['brand_existing'] + stats['brand_new']} (به برند موجود: {stats['brand_existing']}، نیازمند ساخت برند: {stats['brand_new']})",
          f"- نام برند با فاصله اضافه: {stats['brand_whitespace']} محصول ({'، '.join(repr(w) for w in ws)})",
          f"- alt گالری: {stats['images_alt']} عکس در {stats['products_alt']} محصول",
          f"- نام بلندتر از ۶۰ کاراکتر (نیازمند seo_title کوتاه): {stats['long_name']}", "",
          "## برندهایی که باید ساخته شوند (بعد از تأیید نام درست)", *[f"- {b} ({c} محصول)" for b, c in new_brands.most_common()], "",
          "## نیازمند بررسی دستی برند", *sorted({f"- {x['changes']['brand_review']['spec_value']}" for x in fixes if 'brand_review' in x['changes']}), "",
          "## نمونه alt", *[f"- `{x['slug']}` → {x['changes']['gallery_alt'][0]['alt']}" for x in fixes[:5] if 'gallery_alt' in x['changes']], "",
          "جزئیات کامل (media_id و متن alt هر عکس): product_seo_fixes.json — هیچ‌کدام اعمال نشده."]
    (ROOT / "data/reports/product_seo_fixes.md").write_text("\n".join(md))
    print("\n".join(md[:8]))


if __name__ == "__main__":
    main("--refresh" in sys.argv)
