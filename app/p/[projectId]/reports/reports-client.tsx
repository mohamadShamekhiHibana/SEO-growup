"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/client/api";
import { faNum } from "@/lib/intl/fa";
import { formatJalaliDateTime } from "@/lib/intl/jalali";
import type { ReportData } from "./page";

type Report = { id: number; ts: number; data: ReportData; prev: Partial<ReportData> };

function diff(cur: number | null, prev: number | null | undefined): string {
  if (cur == null || prev == null) return "";
  const d = cur - prev;
  if (!d) return "";
  return d > 0 ? ` (+${faNum(d, 1)})` : ` (${faNum(d, 1)})`;
}

export function ReportsClient({ projectId, isAdmin, initial }: { projectId: string; isAdmin: boolean; initial: Report[] }) {
  const router = useRouter();
  const [reports, setReports] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function make() {
    setBusy(true); setErr("");
    try {
      const r = await api<{ report: number } & ReportData>(`/api/projects/${projectId}/reports`, { method: "POST" });
      setReports([{ id: r.report, ts: Date.now() / 1000, data: r, prev: reports[0]?.data || {} }, ...reports]);
      router.refresh();
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "خطا");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      {isAdmin && (
        <div className="row" style={{ gap: 8, margin: "0 0 14px" }}>
          <button type="button" className="btn sm primary" disabled={busy} onClick={make}>
            {busy ? "در حال ساخت..." : "ساخت گزارش جدید"}
          </button>
        </div>
      )}
      {err && <div className="err" role="alert">{err}</div>}
      {!reports.length && <p className="muted">هنوز گزارشی ساخته نشده.</p>}
      <div className="pick-grid">
        {reports.map((r) => (
          <div key={r.id} className="panel">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <strong>{formatJalaliDateTime(r.ts * 1000)}</strong>
              {r.data.score != null && <span className="chip">امتیاز سئو {faNum(r.data.score)}{diff(r.data.score, r.prev.score)}</span>}
            </div>
            <table style={{ width: "100%", marginTop: 8 }}>
              <tbody>
                <tr><td className="muted">مشکل بحرانی / هشدار</td><td>{faNum(r.data.critical)} / {faNum(r.data.warning)}</td></tr>
                <tr><td className="muted">رفع‌شده این هفته</td><td>{faNum(r.data.fixed_week)}</td></tr>
                <tr><td className="muted">کلیک سرچ کنسول (۷ روز)</td><td>{faNum(r.data.clicks)}{diff(r.data.clicks, r.prev.clicks)}</td></tr>
                <tr><td className="muted">نمایش سرچ کنسول (۷ روز)</td><td>{faNum(r.data.impressions)}{diff(r.data.impressions, r.prev.impressions)}</td></tr>
                <tr><td className="muted">آپتایم</td><td>{r.data.uptime != null ? `${faNum(r.data.uptime)}٪` : "—"}</td></tr>
                <tr><td className="muted">سرعت موبایل (PageSpeed)</td><td>{r.data.mobile_speed != null ? faNum(r.data.mobile_speed) : "—"}</td></tr>
                <tr><td className="muted">ایندکس‌شده</td><td>{faNum(r.data.indexed)} از {faNum(r.data.index_checked)}</td></tr>
                <tr><td className="muted">اصلاح اعمال‌شده این هفته</td><td>{faNum(r.data.done_fixes)}</td></tr>
                <tr><td className="muted">کار باز</td><td>{faNum(r.data.tasks_open)}</td></tr>
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}
