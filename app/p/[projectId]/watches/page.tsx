// Same gap as reports: app/api/projects/[id]/watches/route.ts (addWatch()/runWatches() in
// lib/extras.ts) existed with no UI to add a watch or see what changed.
import { notFound, redirect } from "next/navigation";
import { project } from "@/lib/projects";
import { currentUser } from "@/lib/server/current-user";
import { role } from "@/lib/auth";
import { q } from "@/lib/db";
import { WatchesClient } from "./watches-client";

export const dynamic = "force-dynamic";

export default async function WatchesTab({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  const p = project(projectId);
  if (!p) notFound();
  const user = await currentUser();
  if (!user) redirect("/login");
  const isAdmin = role(user, projectId) === "admin";

  const rows = q<{ id: number; mine: string; others: string; changes: string; ts: number }>(
    "SELECT id, mine, others, changes, ts FROM watches WHERE project_id=? ORDER BY id DESC", projectId,
  );
  const watches = rows.map((r) => ({
    id: r.id, mine: r.mine,
    others: JSON.parse(r.others) as string[],
    changes: JSON.parse(r.changes || "[]") as string[],
    ts: r.ts,
  }));

  return (
    <div>
      <div className="page-head"><div className="head-title"><h1>پایش رقبا</h1></div></div>
      <p className="page-note">بررسی تغییر صفحات رقبا (عنوان، حجم متن، تیترهای جدید) نسبت به صفحه خودتان.</p>
      <WatchesClient projectId={projectId} isAdmin={isAdmin} initial={watches} />
    </div>
  );
}
