"""کلاینت حداقلی API استیو (فقط stdlib). خواندن عمومی؛ نوشتن فقط draft."""
import json, os, urllib.error, urllib.parse, urllib.request

BASE = os.environ.get("STEVE_API_URL", "").rstrip("/")
TOKEN = os.environ.get("STEVE_BACKOFFICE_TOKEN", "")


def _req(method, path, params=None, body=None, auth=False):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Accept-Language": "fa", "Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.load(resp).get("data")


def paged(path, key, size=100, **extra):
    page, out = 1, []
    while True:
        d = _req("GET", path, {"page_number": page, "page_size": size, **extra}) or {}
        items = d.get(key) or []
        out += items
        total = (d.get("pagination") or {}).get("total", len(out))
        if not items or len(out) >= total:
            return out
        page += 1


def storefront_products():
    return paged("/product/storefront", "products")


def product_by_slug(slug):
    return _req("GET", f"/product/storefront/get-by-slug/{urllib.parse.quote(slug)}")


def storefront_articles():
    return paged("/article/storefront", "articles")


import pathlib, uuid, mimetypes
_ROOT = pathlib.Path(__file__).resolve().parent.parent
_STATE = _ROOT / "data/state.json"


def upload_media(path, domain="article"):
    """آپلود عکس به رسانه بک‌آفیس (multipart) → media_id"""
    b = uuid.uuid4().hex; p = pathlib.Path(path); data = p.read_bytes()
    parts = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in
                     (("domain", domain), ("is_public", "true"), ("convert_to_webp", "true")))
    parts += (f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{p.name}"\r\nContent-Type: {mimetypes.guess_type(p.name)[0] or "image/png"}\r\n\r\n').encode() + data + f"\r\n--{b}--\r\n".encode()
    r = urllib.request.Request(BASE + "/media/upload", data=parts, method="POST",
                               headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": f"multipart/form-data; boundary={b}"})
    return json.load(urllib.request.urlopen(r, timeout=60))["data"]["id"]


def cover_id():
    """media_id پیش‌فرض (آیکون بدون‌تصویر). اگر قبلی حذف شده باشد دوباره آپلود می‌شود."""
    try: return json.loads(_STATE.read_text())["cover_media_id"]
    except Exception: return refresh_cover()


def refresh_cover():
    mid = upload_media(_ROOT / "assets/placeholder-cover.png")
    _STATE.write_text(json.dumps({"cover_media_id": mid})); return mid


def create_article_draft(a):
    """a: title, slug, body, tags, meta_description, alt. همیشه is_published=False."""
    a = {**a, "is_published": False}
    a.setdefault("media_id", cover_id())
    try:
        return _req("POST", "/article/create", body=a, auth=True)
    except urllib.error.HTTPError as e:
        if e.code == 400 and "media_id" in e.read().decode("utf8", "ignore"):  # کاور پیش‌فرض حذف شده
            a["media_id"] = refresh_cover()
            return _req("POST", "/article/create", body=a, auth=True)
        raise
