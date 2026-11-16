"""حافظه ایجنت‌ها: SQLite (stdlib). تسک، صف تأیید، متریک، یادگیری."""
import sqlite3, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "data/agent.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, agent TEXT, kind TEXT, title TEXT, payload TEXT,
  status TEXT DEFAULT 'pending', result TEXT, created_at TEXT, updated_at TEXT, UNIQUE(agent,kind,title));
CREATE TABLE IF NOT EXISTS proposals(id INTEGER PRIMARY KEY, task_id INTEGER, kind TEXT, target TEXT,
  content TEXT, status TEXT DEFAULT 'pending', note TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS metrics(day TEXT, key TEXT, value REAL, PRIMARY KEY(day,key));
CREATE TABLE IF NOT EXISTS learnings(id INTEGER PRIMARY KEY, day TEXT, topic TEXT, insight TEXT, evidence TEXT);
CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY, day TEXT, what TEXT, hypothesis TEXT, metric TEXT, baseline TEXT, due_day TEXT, status TEXT DEFAULT 'open', result TEXT);
CREATE TABLE IF NOT EXISTS competitor_prices(day TEXT, slug TEXT, source TEXT, low REAL, high REAL, offers INTEGER, PRIMARY KEY(day,slug,source));
"""


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c
