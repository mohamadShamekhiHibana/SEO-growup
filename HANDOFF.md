# پیام‌های آماده برای بقیه (این پروژه هیچ سرویس دیگری را تغییر نداده)

## بک‌اند Steve (Go)
۱) روی `entity.Product` فیلدهای اختیاری با `omitempty` اضافه شود: `seo_title`, `seo_description`, `focus_keyword`, `faq []{question,answer}`؛ و `Alt` روی `ProductGallery`. این‌ها به DTO ادمین (add/update/get) و پاسخ storefront (`/product/storefront/get-by-slug/:slug`) اضافه شوند.
۲) یک نقش ACL به نام `ai_agent` در seeder با مجوزهای: `ViewProduct`, `ListProducts`, `ListArticles`, `ViewArticle`, `CreateArticle`, `UpdateProduct` (فقط فیلدهای SEO). بدون Publish/Delete.
۳) یک کاربر backoffice برای این نقش و توکن JWT بلندمدت (یا endpoint لاگین سرویس) بدهید.
۴) اطلاعات لازم از من: آدرس لاگین backoffice (در routes پیدا نکردم).

## فرانت storefront (Next.js)
بعد از ۱: `pageSeoGenerator` برای محصول از `seo_title`/`seo_description` بخواند (fallback به مقدار فعلی)، `faq` به JSON-LD (FAQPage) اضافه شود، `alt` گالری استفاده شود.

## بک‌آفیس
فرم محصول: فیلدهای seo_title/seo_description/focus_keyword/faq. (اختیاری فاز ۲: صفحه مرور پیشنهادهای AI.)
