#!/usr/bin/env python3
"""مدیر مرکزی سبک: plan / next / done / propose / review / learn / metrics / status.
اجرا داخل Claude Code (بدون API پولی). همه خروجی‌های نوشتنی = proposal یا draft."""
import argparse, json, pathlib, re, sys, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from store.db import conn, now
from lib import jalali

REG = json.load(open(ROOT / "agents/registry.json", encoding="utf8"))
ISSUE_AGENT = "seo"


def add_task(c, agent, kind, title, payload):
    cur = c.execute("INSERT OR IGNORE INTO tasks(agent,kind,title,payload,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                    (agent, kind, title, json.dumps(payload, ensure_ascii=False), now(), now()))
    return cur.rowcount


def cmd_plan(a):
    import subprocess
    try:  # keyword_plan.md همیشه تازه باشد
        print(subprocess.run([sys.executable, str(ROOT / "agents/keywords/refresh.py")], capture_output=True, text=True, timeout=180).stdout.strip())
    except Exception as e:
        print("refresh کلمات کلیدی ناموفق:", str(e)[:60])
    c, n = conn(), 0
    audit = ROOT / "data/reports/seo_audit.json"
    if audit.exists():
        for issue, slugs in json.load(open(audit, encoding="utf8")).items():
            if slugs and issue != "gallery_without_alt":  # alt تا اضافه‌شدن فیلد در API قابل اندازه‌گیری نیست
                n += add_task(c, "seo", "fix", f"{issue}", {"issue": issue, "slugs": slugs[:20], "total": len(slugs)})
    kp = ROOT / "data/reports/keyword_plan.md"
    if kp.exists():
        sec = kp.read_text(encoding="utf8").split("## فرصت‌های محتوایی")[-1].split("\n## ")[0]
        for line in sec.splitlines():
            m = re.match(r"^[۰-۹0-9]+[.)]\s*(.+)", line.strip())
            if m and "✅" not in line:
                n += add_task(c, "content", "article", m.group(1)[:120], {"brief": m.group(1)})
    today = datetime.date.today()
    wk = jalali.iso(jalali.week_start(today))
    nwk = jalali.iso(jalali.week_start(today) + datetime.timedelta(days=7))
    n += add_task(c, "analytics", "weekly_snapshot", wk, {"week": wk})
    n += add_task(c, "instagram", "weekly_plan", nwk, {"week_start": nwk})
    mo = jalali.month_key(today)
    n += add_task(c, "marketing", "campaign_plan", mo, {"month": mo})
    c.commit()
    print(f"{n} تسک جدید")


def cmd_next(a):
    c = conn()
    q = "SELECT * FROM tasks WHERE status='pending'" + (" AND agent=?" if a.agent else "") + " ORDER BY id LIMIT 1"
    r = c.execute(q, (a.agent,) if a.agent else ()).fetchone()
    if not r:
        print("NONE"); return
    c.execute("UPDATE tasks SET status='in_progress',updated_at=? WHERE id=?", (now(), r["id"])); c.commit()
    print(json.dumps({"id": r["id"], "agent": r["agent"], "kind": r["kind"], "title": r["title"],
                      "payload": json.loads(r["payload"]), "skill": REG[r["agent"]]["skill"], "can": REG[r["agent"]]["can"]},
                     ensure_ascii=False, indent=1))


def cmd_done(a):
    c = conn()
    c.execute("UPDATE tasks SET status=?,result=?,updated_at=? WHERE id=?", (a.status, a.result, now(), a.id)); c.commit()
    print("ok")


def cmd_propose(a):
    c = conn()
    c.execute("INSERT INTO proposals(task_id,kind,target,content,created_at) VALUES(?,?,?,?,?)",
              (a.task, a.kind, a.target, a.content, now())); c.commit()
    print("proposal ثبت شد")


def cmd_review(a):
    c = conn()
    if a.action == "list":
        for r in c.execute("SELECT id,kind,target,status,substr(content,1,70) s FROM proposals WHERE status=? ORDER BY id", (a.status,)):
            print(r["id"], r["kind"], r["target"], r["status"], "|", r["s"])
    elif a.action == "show":
        r = c.execute("SELECT * FROM proposals WHERE id=?", (a.id,)).fetchone(); print(dict(r))
    else:
        st = "approved" if a.action == "approve" else "rejected"
        c.execute("UPDATE proposals SET status=?,note=? WHERE id=?", (st, a.note, a.id)); c.commit(); print(st)


def cmd_learn(a):
    c = conn()
    if a.topic:
        c.execute("INSERT INTO learnings(day,topic,insight,evidence) VALUES(?,?,?,?)",
                  (jalali.iso(), a.topic, a.insight, a.evidence)); c.commit(); print("ثبت شد")
    for r in c.execute("SELECT day,topic,insight,evidence FROM learnings ORDER BY id DESC LIMIT 15"):
        print(r["day"], r["topic"], "→", r["insight"], f"({r['evidence']})")


def cmd_metrics(a):
    c = conn()
    for r in c.execute("SELECT day,key,value FROM metrics ORDER BY day DESC,key LIMIT ?", (a.limit,)):
        print(r["day"], r["key"], r["value"])


def cmd_exp(a):
    c = conn()
    if a.action == "add":
        due = jalali.iso(datetime.date.today() + datetime.timedelta(days=a.days))
        c.execute("INSERT INTO experiments(day,what,hypothesis,metric,baseline,due_day) VALUES(?,?,?,?,?,?)",
                  (jalali.iso(), a.what, a.hypothesis, a.metric, a.baseline, due)); c.commit(); print("ثبت شد؛ بررسی در", due)
    elif a.action == "close":
        c.execute("UPDATE experiments SET status='closed',result=? WHERE id=?", (a.result, a.id)); c.commit(); print("بسته شد")
    else:
        q = "SELECT * FROM experiments WHERE status='open'" + (" AND due_day<=?" if a.action == "due" else "") + " ORDER BY due_day"
        for r in c.execute(q, (jalali.iso(),) if a.action == "due" else ()):
            print(r["id"], r["day"], "→", r["due_day"], "|", r["what"], "| فرضیه:", r["hypothesis"], "| معیار:", r["metric"], "| مبنا:", r["baseline"])


def cmd_stats(a):
    c = conn()
    for r in c.execute("SELECT kind,status,count(*) n FROM proposals GROUP BY kind,status ORDER BY kind"):
        print(r["kind"], r["status"], r["n"])


def cmd_status(a):
    c = conn()
    for t, col in (("tasks", "status"), ("proposals", "status")):
        print(t, {r[0]: r[1] for r in c.execute(f"SELECT {col},count(*) FROM {t} GROUP BY {col}")})


p = argparse.ArgumentParser(); s = p.add_subparsers(dest="cmd", required=True)
s.add_parser("plan").set_defaults(f=cmd_plan)
x = s.add_parser("next"); x.add_argument("--agent"); x.set_defaults(f=cmd_next)
x = s.add_parser("done"); x.add_argument("id", type=int); x.add_argument("--status", default="done"); x.add_argument("--result", default=""); x.set_defaults(f=cmd_done)
x = s.add_parser("propose"); x.add_argument("--task", type=int, default=0); x.add_argument("--kind", required=True); x.add_argument("--target", required=True); x.add_argument("--content", required=True); x.set_defaults(f=cmd_propose)
x = s.add_parser("review"); x.add_argument("action", choices=["list", "show", "approve", "reject"]); x.add_argument("id", type=int, nargs="?"); x.add_argument("--status", default="pending"); x.add_argument("--note", default=""); x.set_defaults(f=cmd_review)
x = s.add_parser("learn"); x.add_argument("topic", nargs="?"); x.add_argument("insight", nargs="?"); x.add_argument("evidence", nargs="?", default=""); x.set_defaults(f=cmd_learn)
x = s.add_parser("metrics"); x.add_argument("--limit", type=int, default=30); x.set_defaults(f=cmd_metrics)
x = s.add_parser("exp"); x.add_argument("action", choices=["add", "list", "due", "close"]); x.add_argument("id", type=int, nargs="?"); x.add_argument("--what", default=""); x.add_argument("--hypothesis", default=""); x.add_argument("--metric", default=""); x.add_argument("--baseline", default=""); x.add_argument("--days", type=int, default=14); x.add_argument("--result", default=""); x.set_defaults(f=cmd_exp)
s.add_parser("stats").set_defaults(f=cmd_stats)
s.add_parser("status").set_defaults(f=cmd_status)
a = p.parse_args(); a.f(a)
