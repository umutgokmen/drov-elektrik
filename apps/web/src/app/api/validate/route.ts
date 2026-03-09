import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();

  try {
    const response = await fetch(`${PYTHON_API_URL}/api/v1/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    // Python API not available - return empty result (client-side validation still works)
    return NextResponse.json({
      is_valid: true,
      errors: [],
      warnings: [{ field: "server", message: "Server validasyonu şu an kullanılamıyor" }],
    });
  }
}
