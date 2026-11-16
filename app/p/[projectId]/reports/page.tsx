// app/api/projects/[id]/reports/route.ts (snapshot()+runReport() in lib/extras.ts) existed
// with no UI reading it — same "API built, nothing shows it" gap as settings/fixes earlier.
import { notFound, redirect } from "next/navigation";
import { project } from "@/lib/projects";
import { currentUser } from "@/lib/server/current-user";
import { role } from "@/lib/auth";
import { q } from "@/lib/db";
import { ReportsClient } from "./reports-client";

export const dynamic = "force-dynamic";

export type ReportData = {
  score: number | null; critical: number; warning: number; fixed_week: number;
  clicks: number; impressions: number; gsc_days: number; uptime: number | null;
  mobile_speed: number | null; indexed: number; index_checked: number; done_fixes: number; tasks_open: number;
};

export default async function ReportsTab({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  const p = project(projectId);
  if (!p) notFound();
  const user = await currentUser();
  if (!user) redirect("/login");
  const isAdmin = role(user, projectId) === "admin";

  const rows = q<{ id: number; ts: number; data: string; prev: string }>(
    "SELECT id, ts, data, prev FROM reports WHERE project_id=? ORDER BY id DESC LIMIT 30", projectId,
  );
  const reports = rows.map((r) => ({ id: r.id, ts: r.ts, data: JSON.parse(r.data) as ReportData, prev: JSON.parse(r.prev || "{}") as Partial<ReportData> }));

  return (
    <div>
      <div className="page-head"><div className="head-title"><h1>گزارش هفتگی</h1></div></div>
      <p className="page-note">امتیاز سئو، سرچ کنسول، آپتایم و سرعت — هر گزارش با دوره قبل مقایسه می‌شود.</p>
      <ReportsClient projectId={projectId} isAdmin={isAdmin} initial={reports} />
    </div>
  );
}
