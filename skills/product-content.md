# Skill: محتوای محصول
ورودی: slug محصول (از `seo_audit.json`، اولویت: توضیح کوتاه/خالی).
مراحل: `lib.steve.product_by_slug(slug)` → تولید:
- seo_title (≤۶۰ کاراکتر، بدون نام برند؛ سایت خودش اضافه می‌کند)
- seo_description (۱۲۰–۱۶۰ کاراکتر)
- توضیح ۲۰۰–۴۰۰ کلمه فارسی طبیعی فقط از `specifications`/`variants`
- ۳–۵ پرسش متداول واقعی، alt تصاویر
خروجی: `data/reports/products/<slug>.json` برای بازبینی. تا اضافه‌شدن فیلدهای SEO در بک‌اند (HANDOFF.md) فقط خروجی فایل می‌شود، نه نوشتن در API.
