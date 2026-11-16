#!/usr/bin/env python3
"""ارسال به گروه تلگرام؛ هر آرگومان = یک پیام جدا، با منشن TELEGRAM_MENTION در ابتدا.
python3 scripts/notify_telegram.py [--topic site|instagram] "پیام ۱" "پیام ۲"   |   --file گزارش.md  (کل فایل یک پیام)
اگر توکن/شناسه در .env نباشد بی‌صدا رد می‌شود. فقط متن ساده؛ هرگز توکن، فروش (مگر اجازه صریح)، یا اطلاعات مشتری."""
import json, os, sys, time, urllib.request

tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
if not tok or not chat:
    print("تلگرام تنظیم نشده؛ رد شد"); sys.exit(0)
args = sys.argv[1:]
topic = "site"
if args[:1] == ["--topic"]:
    topic, args = args[1], args[2:]  # site (پیش‌فرض) | instagram
men = os.environ.get("TELEGRAM_MENTION_" + topic.upper(), os.environ.get("TELEGRAM_MENTION", "@ms_Fallah01"))
msgs = [open(args[1], encoding="utf8").read()] if args[:1] == ["--file"] else args
import re
BAD = re.compile(r"(data/|\.md\b|\.py\b|python3|/Users/|\.env|orchestrator|ai-growth-agent|تأیید می‌کنید|تایید می‌کنید|موافقید|کدام را|بگویید تا|اجازه بدهید|نظر شما را)")
for m in msgs:
    m = m.strip()
    if BAD.search(m):
        print("رد شد (سؤال/مسیر فایل/دستور در پیام ممنوع است):", m[:50]); continue
    if men and not all(u in m for u in men.split()):
        m = f"{men}\n{m}"
    for i in range(0, len(m), 3900):
        body = json.dumps({"chat_id": chat, "text": m[i:i + 3900], "disable_web_page_preview": True}).encode()
        r = urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=body, headers={"Content-Type": "application/json"})
        try:
            print(json.load(urllib.request.urlopen(r, timeout=30)).get("ok"))
        except Exception as e:
            print("خطا:", str(e).replace(tok, "***")[:100])
        time.sleep(1)
