#!/usr/bin/env python3
"""ممیزی سئو محصولات و مقالات (فقط خواندنی). خروجی: data/reports/seo_audit.json + خلاصه."""
import json, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib import steve

out = pathlib.Path(__file__).resolve().parent.parent / "data/reports/seo_audit.json"
issues = collections.defaultdict(list)

for p in steve.storefront_products():
    slug = p.get("slug") or p.get("id")
    full = steve.product_by_slug(p["slug"]).get("product", {}) if p.get("slug") else {}
    desc = (full.get("description") or "").strip()
    if len(desc) < 150:
        issues["short_or_empty_description"].append(slug)
    if not full.get("en_title"):
        issues["no_en_title"].append(slug)
    if not full.get("specifications"):
        issues["no_specifications"].append(slug)
    for g in full.get("gallery") or []:
        if not g.get("alt"):
            issues["gallery_without_alt"].append(slug); break

titles = collections.Counter()
import urllib.parse
for a in steve.storefront_articles():
    titles[a.get("title")] += 1
    d = steve._req("GET", "/article/storefront/get-by-slug/" + urllib.parse.quote(a["slug"]))
    a = d.get("article", d)
    md = (a.get("meta_description") or "").strip()
    if "پیشنهادی" in md:
        issues["article_meta_has_leftover_prefix"].append(a.get("slug"))
    if not (120 <= len(md) <= 160):
        issues["article_meta_length_out_of_120_160"].append(a.get("slug"))
    if not a.get("alt"):
        issues["article_image_without_alt"].append(a.get("slug"))
issues["duplicate_article_titles"] = [t for t, c in titles.items() if c > 1]

out.write_text(json.dumps(issues, ensure_ascii=False, indent=2))
for k, v in issues.items():
    print(f"{k}: {len(v)}")
print("->", out)
