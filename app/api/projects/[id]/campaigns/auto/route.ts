import { NextRequest, NextResponse } from "next/server";
import { requireProjectAccess } from "@/lib/access";
import { project } from "@/lib/projects";
import { autoGenerate, get } from "@/lib/campaigns";
import { logActivity } from "@/lib/activity";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id: pid } = await params;
  const gate = requireProjectAccess(req, pid, "edit");
  if ("response" in gate) return gate.response;
  const p = project(pid);
  if (!p) return NextResponse.json({ error: "پروژه پیدا نشد" }, { status: 404 });

  const body = await req.json().catch(() => ({})) as { title?: string };
  const title = String(body.title || "").trim().slice(0, 200) || undefined;

  try {
    const id = await autoGenerate(p, gate.user.name, title);
    logActivity(pid, gate.user.name, "POST", req.nextUrl.pathname);
    return NextResponse.json(get(id));
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message || "خطا" }, { status: 502 });
  }
}
