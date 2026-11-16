This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---

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
