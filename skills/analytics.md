# Skill: تحلیل و یادگیری
1. `python3 agents/analytics/snapshot.py` متریک امروز را ذخیره می‌کند.
2. با `python3 -m orchestrator.cli metrics` روند را ببین و با هفته قبل مقایسه کن.
3. نتیجه را با `python3 -m orchestrator.cli learn "<موضوع>" "<بینش>" "<شاهد عددی>"` ثبت کن (فقط وقتی داده واقعاً چیزی نشان می‌دهد؛ حدس ثبت نکن).
4. اگر یادگیری اولویت‌ها را عوض می‌کند، پیشنهاد تسک بعدی را به کاربر بگو.

## تعریف‌های endpoint فروش (از بک‌اند؛ قبل از مقایسه بخوان)
- واحد: **تومان**. `daily_sales`/`top_products`/`top_categories` فقط سفارش‌های غیرلغو و غیر pending_payment؛ `orders_by_status` همه سفارش‌های ایجادشده در بازه (با لغو و pending). جمعشان برابر نیست.
- `non_catalog_revenue`: فاکتور دستی بدون محصول (مثل تعمیر) — در top_products نمی‌آید. فروش کاتالوگ = daily_sales − non_catalog_revenue.
- لغوها فعلاً عمدتاً تستی‌اند (`unknown` = قبل از ثبت علت).
