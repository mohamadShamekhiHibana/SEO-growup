# AI Growth Agent — فاز ۱ (سئو و محتوا)

اجرا با Claude Code (اکانت Pro)، بدون سرور دائمی. فقط API استیو را می‌خواند و **فقط draft** می‌نویسد.

## راه‌اندازی
1. `cp .env.example .env` و مقادیر را پر کنید؛ `set -a; source .env; set +a`
2. ممیزی: `python3 scripts/audit_seo.py` ← `data/reports/seo_audit.json`
3. در Claude Code داخل همین پوشه، فرمان‌های `skills/*.md` را اجرا کنید (مثلاً «طبق skills/keyword-research.md کار کن»).

## جریان کار
audit → keyword-research (ورودی: CSV سرچ‌کنسول در `data/inbox/`) → product-content / article-writer → draft → تأیید انسانی در بک‌آفیس → انتشار.

## قوانین ثابت
- هیچ‌چیز مستقیم منتشر نمی‌شود (`is_published=false`).
- محتوا فقط از مشخصات ثبت‌شده محصول؛ ادعای ساختگی (گارانتی، قیمت، موجودی) ممنوع.
- فقط فارسی. بدون تکرار محتوا بین صفحه‌ها.

## مدیر مرکزی (orchestrator)
`python3 -m orchestrator.cli plan` تسک‌ها را از ممیزی و keyword_plan می‌سازد؛ `next` تسک بعدی و skill مربوط را می‌دهد؛ `review list|approve|reject` صف تأیید؛ `learn` و `metrics` حافظه یادگیری. جزئیات: CLAUDE.md.
