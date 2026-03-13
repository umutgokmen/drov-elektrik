import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { holes_top, holes_bottom, holes_left, holes_right, switchgear, cover_elements, ...rest } = body;

  const response = await fetch(`${PYTHON_API_URL}/api/v1/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer dev" },
    body: JSON.stringify({
      configuration: {
        ...rest,
        holes_top_spec: holes_top,
        holes_bottom_spec: holes_bottom,
        holes_left_spec: holes_left,
        holes_right_spec: holes_right,
      },
      format: "dxf",
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    return NextResponse.json(error, { status: response.status });
  }

  const dxfBuffer = await response.arrayBuffer();
  return new NextResponse(dxfBuffer, {
    headers: {
      "Content-Type": "application/dxf",
      "Content-Disposition": `attachment; filename="drawing-${body.box_id}.dxf"`,
    },
  });
}
