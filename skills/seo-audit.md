# Skill: اصلاح مشکلات ممیزی سئو
ورودی: payload تسک (نوع مشکل + slugها). فقط بخوان و پیشنهاد بده.
برای هر slug: وضعیت فعلی را از API بخوان، اصلاح مشخص بنویس، با `python3 -m orchestrator.cli propose` به صف تأیید بفرست (kind=seo_fix، target=slug، content=JSON پیشنهاد). هیچ‌چیز مستقیم اعمال نشود مگر meta مقاله با تأیید صریح کاربر.

## ممیزی کامل (هفتگی، شنبه)
1. `python3 scripts/audit_technical.py` → `technical_audit.json`: sitemap، کد وضعیت، title/meta/canonical/H1، JSON-LD، og:image، سرعت، لینک شکسته. مشکل‌های کد سایت را فقط به‌صورت پیام آماده برای تیم storefront گزارش کن (storefront فقط‌خواندنی است).
2. `python3 scripts/product_seo_fixes.py --refresh` → `product_seo_fixes.md/json`: برند «متفرقه»، alt گالری، نام‌های بلند. فقط پیشنهاد؛ اعمال با تأیید کاربر.
3. `python3 scripts/internal_links.py` (بعد از به‌روزکردن `articles_links.json`) → `internal_links.md`: مقاله‌های بدون لینک محصول/مقاله.
4. مقایسه با هفته قبل و ثبت در گزارش روزانه؛ کار جدید = تسک در `cli plan`.
