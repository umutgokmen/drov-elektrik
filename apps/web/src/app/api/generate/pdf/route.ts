import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const response = await fetch(`${PYTHON_API_URL}/api/v1/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer dev" },
    body: JSON.stringify({ ...body, format: "pdf" }),
  });

  if (!response.ok) {
    const error = await response.json();
    return NextResponse.json(error, { status: response.status });
  }

  const pdfBuffer = await response.arrayBuffer();
  return new NextResponse(pdfBuffer, {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="drawing-${body.box_id}.pdf"`,
    },
  });
}
