import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { holes_top, holes_bottom, holes_left, holes_right, switchgear, cover_elements, ...rest } = body;

  const switchgearByRail: Record<number, object[]> = {};
  for (const item of (switchgear || [])) {
    const ri = item.railIndex ?? 0;
    if (!switchgearByRail[ri]) switchgearByRail[ri] = [];
    switchgearByRail[ri].push({
      component_id: item.componentId,
      quantity: item.quantity ?? 1,
      ...(item.currentRating !== undefined && { current_rating: item.currentRating }),
      ...(item.coilVoltage !== undefined && { coil_voltage: item.coilVoltage }),
    });
  }
  const switchgear_rails = Object.entries(switchgearByRail).map(([ri, components]) => ({
    rail_index: Number(ri),
    components,
  }));

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
      switchgear_rails,
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
