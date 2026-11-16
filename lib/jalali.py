"""تاریخ شمسی (بدون وابستگی). CLI: python3 -m lib.jalali today|week|month|plus <days>"""
import datetime, sys

MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
DAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]  # weekday(): دوشنبه=0


def to_jalali(d):
    gy, gm, gd = d.year, d.month, d.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053); days %= 12053
    jy += 4 * (days // 1461); days %= 1461
    if days > 365:
        jy += (days - 1) // 365; days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


def iso(d=None):
    y, m, dd = to_jalali(d or datetime.date.today()); return f"{y}-{m:02d}-{dd:02d}"


def human(d=None):
    d = d or datetime.date.today(); y, m, dd = to_jalali(d)
    return f"{DAYS[d.weekday()]} {dd} {MONTHS[m-1]} {y}"


def week_start(d=None):
    """شروع هفته = شنبه"""
    d = d or datetime.date.today()
    return d - datetime.timedelta(days=(d.weekday() - 5) % 7)


def month_key(d=None):
    y, m, _ = to_jalali(d or datetime.date.today()); return f"{y}-{m:02d}"


if __name__ == "__main__":
    a = sys.argv[1:] or ["today"]; t = datetime.date.today()
    if a[0] == "today": print(iso(t), "|", human(t))
    elif a[0] == "week": print(iso(week_start(t)))
    elif a[0] == "nextweek": print(iso(week_start(t) + datetime.timedelta(days=7)))
    elif a[0] == "month": print(month_key(t))
    elif a[0] == "plus": d = t + datetime.timedelta(days=int(a[1])); print(iso(d), "|", human(d))
    elif a[0] == "day": print(to_jalali(t)[2])
