#!/usr/bin/env python3
"""ممیزی سئوی فنی سایت عمومی (فقط خواندنی، آهسته: ۱ درخواست در ثانیه).
robots + sitemap + نمونه صفحات هر نوع → title/meta/canonical/h1/JSON-LD/OG/noindex/alt/سرعت/لینک شکسته.
خروجی: data/reports/technical_audit.json + خلاصه."""
import json, re, sys, time, pathlib, random, collections, urllib.request, urllib.error, urllib.parse
from html.parser import HTMLParser

SITE = "https://stevemobile.com"
UA = "Mozilla/5.0 (Macintosh) SteveSEOAudit/1.0"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data/reports/technical_audit.json"
PER_TYPE = int(sys.argv[1]) if len(sys.argv) > 1 else 6


def fetch(url, head=False):
    t0 = time.time()
    url = urllib.parse.quote(urllib.parse.unquote(url), safe=":/?&=#%")  # Persian slugs
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD" if head else "GET")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            body = b"" if head else r.read()
            return r.status, body.decode("utf-8", "replace"), time.time() - t0, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", time.time() - t0, url
    except Exception as e:
        return 0, str(e), time.time() - t0, url
    finally:
        time.sleep(1)


def U(u):
    return urllib.parse.unquote(u).rstrip("/")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.meta, self.links, self.h1, self.imgs, self.ld, self.a = "", {}, {}, [], [], [], set()
        self._in = None
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self._in, self._buf = "title", ""
        elif tag == "h1": self._in, self._buf = "h1", ""
        elif tag == "script" and a.get("type") == "application/ld+json": self._in, self._buf = "ld", ""
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k: self.meta[k.lower()] = a.get("content") or ""
        elif tag == "link" and a.get("rel"):
            self.links.setdefault(a["rel"].lower(), []).append(a.get("href") or "")
        elif tag == "img": self.imgs.append(a)
        elif tag == "a" and a.get("href"): self.a.add(a["href"])

    def handle_data(self, d):
        if self._in: self._buf += d

    def handle_endtag(self, tag):
        if self._in == "title" and tag == "title": self.title = self._buf.strip(); self._in = None
        elif self._in == "h1" and tag == "h1": self.h1.append(re.sub(r"\s+", " ", self._buf).strip()); self._in = None
        elif self._in == "ld" and tag == "script": self.ld.append(self._buf); self._in = None


def ld_types(blocks):
    types = []
    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            if t: types.extend(t if isinstance(t, list) else [t])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    for b in blocks:
        try: walk(json.loads(b))
        except Exception: types.append("INVALID_JSON")
    return sorted(set(types))


def kind(url):
    p = urllib.parse.urlparse(url).path
    if p in ("", "/"): return "home"
    seg = p.strip("/").split("/")
    if seg[0] == "blog": return "article" if len(seg) > 1 else "blog"
    if seg[0] == "product": return "product" if len(seg) == 2 and seg[1] not in ("price-range",) else "listing"
    if seg[0] in ("category", "brand", "categories"): return "listing"
    return "static"


def main():
    report = {"site": SITE, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "site_issues": [], "pages": [], "issues": collections.defaultdict(list)}
    st, robots, _, _ = fetch(SITE + "/robots.txt")
    report["robots"] = {"status": st, "has_sitemap": "sitemap:" in robots.lower()}
    st, xml, _, _ = fetch(SITE + "/sitemap.xml")
    urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
    if "<sitemapindex" in xml:
        subs, urls = urls, []
        for s in subs:
            _, x, _, _ = fetch(s)
            urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", x)
    report["sitemap"] = {"status": st, "urls": len(urls), "by_kind": collections.Counter(kind(u) for u in urls)}
    if not any(kind(u) == "product" for u in urls): report["site_issues"].append("sitemap_has_no_product_urls")
    if not any(kind(u) == "article" for u in urls): report["site_issues"].append("sitemap_has_no_article_urls")
    if len(urls) != len(set(urls)): report["site_issues"].append("sitemap_duplicate_urls")

    groups = collections.defaultdict(list)
    for u in urls: groups[kind(u)].append(u)
    random.seed(7)
    sample = [u for k, lst in groups.items() for u in (lst if len(lst) <= PER_TYPE else random.sample(lst, PER_TYPE))]

    seen_titles, seen_desc = collections.defaultdict(list), collections.defaultdict(list)
    internal = set()
    for url in sample:
        st, html, sec, final = fetch(url)
        rec = {"url": url, "kind": kind(url), "status": st, "seconds": round(sec, 2), "kb": len(html.encode()) // 1024}
        if U(final) != U(url): rec["redirected_to"] = final
        report["pages"].append(rec)
        iss = report["issues"]
        if st != 200: iss["non_200_in_sitemap"].append(f"{st} {url}"); continue
        p = Page(); p.feed(html)
        canon = (p.links.get("canonical") or [""])[0]
        desc = p.meta.get("description", "")
        robots_meta = p.meta.get("robots", "")
        rec.update(title=p.title, title_len=len(p.title), desc_len=len(desc), canonical=canon, h1=p.h1[:3],
                   jsonld=ld_types(p.ld), og_image=bool(p.meta.get("og:image")), robots=robots_meta,
                   imgs=len(p.imgs), imgs_no_alt=sum(1 for i in p.imgs if not (i.get("alt") or "").strip()),
                   hreflang=bool(p.links.get("alternate")))
        if sec > 3: iss["slow_over_3s"].append(f"{sec:.1f}s {url}")
        if rec["kb"] > 300: iss["html_over_300kb"].append(f"{rec['kb']}KB {url}")
        if not p.title: iss["missing_title"].append(url)
        elif not (25 <= len(p.title) <= 65): iss["title_length_out_of_25_65"].append(f"{len(p.title)} {url}")
        if not desc: iss["missing_meta_description"].append(url)
        elif not (70 <= len(desc) <= 165): iss["meta_description_length"].append(f"{len(desc)} {url}")
        if not canon: iss["missing_canonical"].append(url)
        elif U(canon) != U(url): iss["canonical_points_elsewhere"].append(f"{url} -> {canon}")
        if len(p.h1) != 1: iss["h1_count_not_1"].append(f"{len(p.h1)} {url}")
        if "noindex" in robots_meta.lower(): iss["noindex_in_sitemap"].append(url)
        if not p.meta.get("og:image"): iss["missing_og_image"].append(url)
        if rec["imgs_no_alt"]: iss["img_without_alt"].append(f"{rec['imgs_no_alt']}/{rec['imgs']} {url}")
        need = {"product": "Product", "article": "Article", "home": "Organization"}.get(rec["kind"])
        if need and not any(need in t for t in rec["jsonld"]): iss[f"missing_jsonld_{need}"].append(url)
        if rec["kind"] in ("product", "article", "listing") and not any("Breadcrumb" in t for t in rec["jsonld"]): iss["missing_jsonld_BreadcrumbList"].append(url)
        if p.title: seen_titles[p.title].append(url)
        if desc: seen_desc[desc].append(url)
        for h in p.a:
            full = urllib.parse.unquote(urllib.parse.urljoin(url, h.split("#")[0]))
            if full.startswith(SITE) and not any(x in full for x in ("/dashboard", "/checkout", "/auth", "/api", "/cart")): internal.add(full)

    report["issues"]["duplicate_titles"] = [f"{t} ({len(u)})" for t, u in seen_titles.items() if len(u) > 1]
    report["issues"]["duplicate_descriptions"] = [f"{len(u)} pages" for d, u in seen_desc.items() if len(u) > 1]
    sitemap_set = {U(u) for u in urls}
    orphan_links = sorted(u for u in internal if U(u) not in sitemap_set and kind(u) in ("product", "article"))
    report["linked_but_not_in_sitemap"] = orphan_links[:50]
    # Broken internal links (sample, HEAD)
    checked = {U(p["url"]) for p in report["pages"]}
    for u in sorted(x for x in internal if U(x) not in checked)[:40]:
        st, _, _, _ = fetch(u, head=True)
        if st >= 400 or st == 0: report["issues"]["broken_internal_links"].append(f"{st} {u}")

    report["issues"] = {k: v for k, v in report["issues"].items() if v}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=dict))
    print("sitemap:", report["sitemap"]["urls"], dict(report["sitemap"]["by_kind"]), "| site:", report["site_issues"])
    print("pages checked:", len(report["pages"]), "| median s:", sorted(p["seconds"] for p in report["pages"])[len(report["pages"]) // 2])
    for k, v in report["issues"].items(): print(f"{k}: {len(v)}")
    print("linked_but_not_in_sitemap:", len(orphan_links))
    print("->", OUT)


if __name__ == "__main__":
    main()
