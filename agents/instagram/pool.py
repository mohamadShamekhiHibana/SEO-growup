#!/usr/bin/env python3
"""منبع ایده اینستاگرام: مقاله‌ها و محصولات موجودِ واقعی که هنوز پست نشده‌اند → data/reports/instagram_pool.json"""
import json, pathlib, random, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import steve
from store.db import conn

steve.BASE = steve.BASE or "https://api.stevemobile.com"
SITE = "https://stevemobile.com"
used = {r["target"] for r in conn().execute("SELECT target FROM proposals WHERE kind='ig_post'")}

articles = []
for a in steve.storefront_articles():
    if a["slug"] in used:
        continue
    articles.append({"type": "article", "slug": a["slug"], "title": a["title"].strip(), "tags": a.get("tags"),
                     "image": a.get("media_url"), "url": f"{SITE}/blog/{a['slug']}"})

products = []
for p in steve.storefront_products():
    if p["slug"] in used:
        continue
    vs = [v for v in p.get("variant") or [] if (v.get("quantity") or 0) > 0]
    img = next((g["url"] for g in p.get("gallery") or [] if g.get("is_primary")), None) or \
          next((g["url"] for g in p.get("gallery") or []), None)
    if not vs or not img:
        continue
    colors = [x["label"] for v in vs for x in v.get("variant_attribute") or [] if x.get("key") == "رنگ"]
    products.append({"type": "product", "slug": p["slug"], "name": p["name"].strip(), "colors": colors,
                     "image": img, "url": f"{SITE}/product/{p['slug']}",
                     "specs": {s["key"]: s["value"] for s in p.get("specifications") or [] if s.get("value") not in (None, "", "-")}})
random.seed(len(used))
random.shuffle(products)
out = {"articles": articles[:10], "products": sorted(products[:30], key=lambda x: -len(x["colors"]))[:10]}
(ROOT / "data/reports/instagram_pool.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(articles), "مقاله،", len(products), "محصول موجود →", "data/reports/instagram_pool.json")
