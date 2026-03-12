import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const response = await fetch(`${PYTHON_API_URL}/api/v1/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer dev" },
    body: JSON.stringify({ ...body, format: "dxf" }),
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
