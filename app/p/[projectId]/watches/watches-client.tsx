"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/client/api";
import { faNum } from "@/lib/intl/fa";
import { formatJalaliDateTime } from "@/lib/intl/jalali";

type Watch = { id: number; mine: string; others: string[]; changes: string[]; ts: number };

export function WatchesClient({ projectId, isAdmin, initial }: { projectId: string; isAdmin: boolean; initial: Watch[] }) {
  const router = useRouter();
  const [watches, setWatches] = useState(initial);
  const [mine, setMine] = useState("");
  const [others, setOthers] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function add() {
    setBusy(true); setErr("");
    try {
      const othersList = others.split("\n").map((x) => x.trim()).filter(Boolean);
      const r = await api<{ id: number }>(`/api/projects/${projectId}/watches`, { method: "POST", body: { mine, others: othersList } });
      setWatches([{ id: r.id, mine, others: othersList, changes: [], ts: 0 }, ...watches]);
      setMine(""); setOthers("");
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
        <div className="panel" style={{ marginBottom: 14 }}>
          <h3>افزودن پایش جدید</h3>
          <div className="form-grid">
            <div className="field full"><label>آدرس صفحه خودتان</label><input className="mono ltr" value={mine} onChange={(e) => setMine(e.target.value)} placeholder="https://..." /></div>
            <div className="field full"><label>آدرس رقبا (هر خط یکی، حداکثر ۵)</label><textarea className="mono ltr" value={others} onChange={(e) => setOthers(e.target.value)} placeholder="https://..." /></div>
            <div className="full"><button type="button" className="btn sm primary" disabled={busy} onClick={add}>{busy ? "در حال افزودن..." : "افزودن پایش"}</button></div>
          </div>
        </div>
      )}
      {err && <div className="err" role="alert">{err}</div>}
      {!watches.length && <p className="muted">هنوز پایشی اضافه نشده.</p>}
      <div className="pick-grid">
        {watches.map((w) => (
          <div key={w.id} className="panel">
            <div className="url">{w.mine}</div>
            <div className="muted small" style={{ marginTop: 4 }}>رقبا: {w.others.join("، ")}</div>
            <div className="muted small" style={{ marginTop: 4 }}>{w.ts ? `آخرین بررسی: ${formatJalaliDateTime(w.ts * 1000)}` : "هنوز بررسی نشده"}</div>
            {w.changes.length > 0 ? (
              <ul style={{ marginTop: 8, paddingInlineStart: 18 }}>
                {w.changes.map((c, i) => <li key={i} className="muted small">{c}</li>)}
              </ul>
            ) : (
              <p className="muted small" style={{ marginTop: 8 }}>{w.ts ? "تغییری نسبت به بار قبل نبود." : "در صف اولین بررسی."}</p>
            )}
          </div>
        ))}
      </div>
      {watches.length > 0 && <p className="muted small" style={{ marginTop: 10 }}>{faNum(watches.length)} پایش ثبت‌شده.</p>}
    </div>
  );
}
