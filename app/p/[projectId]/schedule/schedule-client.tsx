"use client";
import { useState } from "react";
import { api, ApiError } from "@/lib/client/api";
import { formatJalaliDateTime } from "@/lib/intl/jalali";

type JobDesc = { key: string; label: string; about: string; min_hours: number; on: boolean; hours: number; at: number | null; idle?: boolean; last: number | null; next: number | null };

export function ScheduleClient({ projectId, initialJobs, isAdmin }: { projectId: string; initialJobs: JobDesc[]; isAdmin: boolean }) {
  const [jobs, setJobs] = useState(initialJobs);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);

  async function toggle(key: string, on: boolean) {
    setJobs(jobs.map((j) => (j.key === key ? { ...j, on } : j)));
    try {
      await api(`/api/projects/${projectId}/schedule`, { method: "POST", body: { [key]: { on } } });
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "خطا");
    }
  }

  async function runNow(kind: string) {
    setErr(""); setBusy(kind); setMsg((m) => ({ ...m, [kind]: "" }));
    try {
      const res = await api<{ queued: boolean }>(`/api/projects/${projectId}/run`, { method: "POST", body: { kind } });
      setMsg((m) => ({ ...m, [kind]: res.queued ? "در صف قرار گرفت — نتیجه را در «فعالیت و کارها» ببین." : "از قبل در صف بود." }));
    } catch (e) {
      setMsg((m) => ({ ...m, [kind]: e instanceof ApiError ? e.message : "خطا" }));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      {err && <div className="err" role="alert">{err}</div>}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead><tr><th>کار</th><th>فعال</th><th>آخرین اجرا</th><th>اجرای بعدی</th><th></th></tr></thead>
        <tbody>
          {jobs.map((j) => (
            <tr key={j.key} style={{ borderTop: "1px solid #333" }}>
              <td>{j.label}<div style={{ fontSize: 11, opacity: 0.6 }}>{j.about}</div></td>
              <td>
                <input type="checkbox" checked={j.on} disabled={!isAdmin} onChange={(e) => toggle(j.key, e.target.checked)} />
              </td>
              <td>{j.last ? formatJalaliDateTime(j.last * 1000) : "—"}</td>
              <td>{j.idle ? "غیرفعال" : j.next ? formatJalaliDateTime(j.next * 1000) : "—"}</td>
              <td>
                {isAdmin && j.key !== "uptime" && (
                  <div className="row" style={{ gap: 6 }}>
                    <button className="btn sm" disabled={busy === j.key} onClick={() => runNow(j.key)}>
                      {busy === j.key ? "در حال ارسال..." : "اجرای الان"}
                    </button>
                    {msg[j.key] && <span className="muted small">{msg[j.key]}</span>}
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted small">کارهایی که هنوز در این نسخه پیاده نشده‌اند، بعد از اجرا پیام خطای روشن در تاریخچه می‌گذارند؛ موفق فرض نمی‌شوند.</p>
    </div>
  );
}
