#!/usr/bin/env python3
"""ساخت عکس برند استیو از عکس‌های واقعی محصول (بدون هوش مصنوعی، رایگان، با Chrome headless).

قالب‌ها: cover (کاور مقاله ۱۲۰۰×۶۷۵) | og (۱۲۰۰×۶۳۰) | post (اینستاگرام ۱۰۸۰×۱۳۵۰) | story (۱۰۸۰×۱۹۲۰)
نمونه:
  python3 scripts/make_image.py --template cover --title "راهنمای خرید قاب آیفون ۱۷" \
      --subtitle "جنس، مگ‌سیف و محافظت دوربین" --badge "راهنمای خرید" \
      --product iPhone-17-normal-MagSafe-Case --product VIP-MAX-...  --out data/reports/images/x.png
عکس محصول فقط از gallery واقعی API (یا --image با URL مستقیم). متن روی عکس فقط از ورودی؛ قیمت/ادعا اضافه نمی‌شود.
"""
import argparse, html, pathlib, subprocess, sys, tempfile, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SIZES = {"cover": (1200, 675), "og": (1200, 630), "post": (1080, 1350), "story": (1080, 1920)}
THEMES = {  # از توکن‌های storefront (_theme.css)
    "brand": ("#2d2566", "#5a4fcf", "#ed1944", "#ffffff"),
    "light": ("#f6f6ff", "#ddd7ff", "#5a4fcf", "#2d2566"),
    "dark": ("#0e0b24", "#2d2566", "#ed1944", "#ffffff"),
}


def product_images(slug, n):
    from lib import steve
    p = steve.product_by_slug(slug).get("product", {})
    g = sorted(p.get("gallery") or [], key=lambda x: not x.get("is_primary"))
    if not g: sys.exit(f"محصول «{slug}» عکس ندارد یا پیدا نشد")
    return [x["url"] for x in g[:n]], p.get("name") or slug


def build_html(t, w, h, title, subtitle, badge, images, theme, footer):
    bg1, bg2, accent, fg = THEMES[theme]
    vertical = h > w
    fonts = (ROOT / "assets/fonts").as_uri()
    logo = (ROOT / "assets/brand/logo.png").as_uri()
    n = len(images)
    title_size = {"cover": 64, "og": 60, "post": 84, "story": 96}[t]
    if len(title) > 40: title_size = int(title_size * 0.8)
    if len(title) > 70: title_size = int(title_size * 0.82)
    imgs = "".join(f'<div class="ph" style="--i:{i}"><img src="{html.escape(u)}" alt=""></div>' for i, u in enumerate(images))
    return f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Yekan; src: url('{fonts}/yekan-regular.woff'); font-weight: 400; }}
@font-face {{ font-family: Yekan; src: url('{fonts}/yekan-bold.woff'); font-weight: 700; }}
@font-face {{ font-family: Yekan; src: url('{fonts}/yekan-fat.woff'); font-weight: 900; }}
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: {w}px; height: {h}px; overflow: hidden; }}
body {{ font-family: Yekan, sans-serif; color: {fg};
  background: radial-gradient(circle at {'50% 30%' if vertical else '22% 50%'}, {bg2} 0%, {bg1} 70%);
  display: flex; flex-direction: {'column' if vertical else 'row'}; padding: {'90px 80px 110px' if vertical else '64px 72px'}; gap: {'48px' if vertical else '40px'}; position: relative; }}
body::before {{ content: ''; position: absolute; inset: 0; background-image: radial-gradient(rgba(255,255,255,.07) 1.5px, transparent 1.5px); background-size: 28px 28px; }}
.text {{ flex: {'0 0 auto' if vertical else '1 1 52%'}; display: flex; flex-direction: column; justify-content: {'flex-start' if vertical else 'center'}; gap: 22px; position: relative; z-index: 1; {'order: -1;' if vertical else ''} }}
.logo {{ height: {80 if vertical else 54}px; align-self: flex-start; background: #fff; padding: {14 if vertical else 10}px {22 if vertical else 16}px; border-radius: 16px; box-sizing: content-box; }}
.badge {{ align-self: flex-start; background: {accent}; color: #fff; font-weight: 700; font-size: {34 if vertical else 26}px; padding: 6px 24px; border-radius: 99px; }}
h1 {{ font-weight: 900; font-size: {title_size}px; line-height: 1.35; text-wrap: balance; }}
p {{ font-size: {40 if vertical else 30}px; opacity: .85; line-height: 1.6; }}
.media {{ flex: 1 1 {'0' if vertical else '48%'}; position: relative; z-index: 1; display: {'grid' if n == 1 else 'flex'}; place-items: center; align-items: center; gap: 18px; min-height: 0; }}
.ph:nth-child(2):not(:last-child) {{ transform: scale(1.12); z-index: 2; }}
.ph {{ background: #fff; border-radius: 28px; box-shadow: 0 30px 60px rgba(0,0,0,.35); border: 8px solid #fff; display: grid; place-items: center; overflow: hidden;
  {('height: ' + ('100%' if n == 1 else '72%') + '; width: auto; max-width: 100%;') if vertical else ('width: ' + ('86%' if n == 1 else '62%') + ';')} aspect-ratio: 1; grid-area: 1 / 1;
  {'' if n == 1 else 'flex: 1 1 0; width: auto; height: auto; max-width: none;'} }}
.ph img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 20px; }}
.foot {{ position: absolute; bottom: {44 if vertical else 26}px; inset-inline: 0; text-align: center; font-size: {30 if vertical else 20}px; opacity: .7; z-index: 1; direction: ltr; }}
</style></head><body>
<div class="text"><img class="logo" src="{logo}" alt="">{f'<span class="badge">{html.escape(badge)}</span>' if badge else ''}<h1>{html.escape(title)}</h1>{f'<p>{html.escape(subtitle)}</p>' if subtitle else ''}</div>
<div class="media">{imgs}</div>
{f'<div class="foot">{html.escape(footer)}</div>' if footer else ''}
</body></html>"""


def render(html_text, w, h, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "page.html"
        f.write_text(html_text, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h}", "--virtual-time-budget=8000", "--allow-file-access-from-files",
                        f"--user-data-dir={d}/profile", f"--screenshot={out}", f.as_uri()],
                       check=True, capture_output=True, timeout=90)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", choices=SIZES, default="cover")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--badge", default="")
    ap.add_argument("--product", action="append", default=[], help="slug محصول (تا ۳ بار)")
    ap.add_argument("--image", action="append", default=[], help="URL مستقیم عکس")
    ap.add_argument("--theme", choices=THEMES, default="brand")
    ap.add_argument("--footer", default="stevemobile.com")
    ap.add_argument("--out")
    a = ap.parse_args()
    images = list(a.image)
    for s in a.product[:3]:
        urls, _ = product_images(s, 1)
        images += urls
    if not images: sys.exit("حداقل یک --product یا --image لازم است")
    images = images[:3]
    w, h = SIZES[a.template]
    if not a.out:
        from lib import jalali
        slug = re.sub(r"[^\w-]+", "-", a.title)[:40].strip("-")
        a.out = f"data/reports/images/{jalali.iso()}_{a.template}_{slug}.png"
    out = render(build_html(a.template, w, h, a.title, a.subtitle, a.badge, images, a.theme, a.footer), w, h, ROOT / a.out)
    print(out)


if __name__ == "__main__":
    main()
