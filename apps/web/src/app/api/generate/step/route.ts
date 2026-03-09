import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();

  const response = await fetch(`${PYTHON_API_URL}/api/v1/generate-cad`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json();
    return NextResponse.json(error, { status: response.status });
  }

  const stepBuffer = await response.arrayBuffer();
  return new NextResponse(stepBuffer, {
    headers: {
      "Content-Type": "application/step",
      "Content-Disposition": `attachment; filename="model-${body.box_id}.step"`,
    },
  });
}
