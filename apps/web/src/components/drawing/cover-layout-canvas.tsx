"use client";

import type { BoxModel, CoverElementSpec } from "@drov/shared";
import { COVER_ELEMENTS_CATALOG } from "@drov/shared";
import type { CoverElement } from "@/stores/configuration-store";

interface CoverLayoutCanvasProps {
  box: BoxModel;
  coverElements: CoverElement[];
}

export function CoverLayoutCanvas({ box, coverElements }: CoverLayoutCanvasProps) {
  const plateW = box.mountingPlateX;
  const plateH = box.mountingPlateY;

  if (!plateW || !plateH) {
    return (
      <div className="flex h-full min-h-[400px] items-center justify-center text-sm text-muted-foreground">
        Bu model için kapak boyut bilgisi yok
      </div>
    );
  }

  // Scale to fit
  const maxDim = Math.max(plateW, plateH);
  const canvasSize = 440;
  const margin = 40;
  const s = (canvasSize - 2 * margin) / maxDim;
  const ox = margin + (canvasSize - 2 * margin - plateW * s) / 2;
  const oy = margin + (canvasSize - 2 * margin - plateH * s) / 2;

  const getCatalogItem = (elementId: string): CoverElementSpec | undefined =>
    COVER_ELEMENTS_CATALOG.find((c) => c.id === elementId);

  return (
    <svg viewBox={`0 0 ${canvasSize} ${canvasSize}`} className="h-full w-full">
      <rect width="100%" height="100%" fill="#ffffff" rx="4" />

      {/* Mounting plate outline */}
      <rect
        x={ox}
        y={oy}
        width={plateW * s}
        height={plateH * s}
        fill="#f8fafc"
        stroke="#334155"
        strokeWidth={1.5}
      />

      {/* Mounting plate dimensions */}
      <text x={ox + (plateW * s) / 2} y={oy - 8} textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="'Helvetica Neue', sans-serif">
        {plateW}mm
      </text>
      <text
        x={ox - 8}
        y={oy + (plateH * s) / 2}
        textAnchor="middle"
        fill="#64748b"
        fontSize="9"
        fontFamily="'Helvetica Neue', sans-serif"
        transform={`rotate(-90, ${ox - 8}, ${oy + (plateH * s) / 2})`}
      >
        {plateH}mm
      </text>

      {/* Center crosshairs */}
      <line
        x1={ox}
        y1={oy + (plateH * s) / 2}
        x2={ox + plateW * s}
        y2={oy + (plateH * s) / 2}
        stroke="#e2e8f0"
        strokeWidth={0.5}
        strokeDasharray="4,4"
      />
      <line
        x1={ox + (plateW * s) / 2}
        y1={oy}
        x2={ox + (plateW * s) / 2}
        y2={oy + plateH * s}
        stroke="#e2e8f0"
        strokeWidth={0.5}
        strokeDasharray="4,4"
      />

      {/* Cover elements */}
      {coverElements.map((el, i) => {
        const spec = getCatalogItem(el.elementId);
        if (!spec) return null;

        const elX = ox + el.x * s;
        const elY = oy + el.y * s;
        const elW = (spec.cutoutWidth || 22) * s;
        const elH = (spec.cutoutHeight || 22) * s;
        const bezelW = (spec.bezelWidth || 30) * s;
        const bezelH = (spec.bezelHeight || 30) * s;

        const isCircular = spec.category === "pushbutton" || spec.category === "selector_switch" || spec.category === "indicator_lamp" || spec.category === "emergency_stop";

        return (
          <g key={i}>
            {isCircular ? (
              <>
                {/* Bezel */}
                <circle cx={elX} cy={elY} r={bezelW / 2} fill="#e2e8f0" stroke="#475569" strokeWidth={0.8} />
                {/* Cutout */}
                <circle cx={elX} cy={elY} r={elW / 2} fill={spec.color || "#94a3b8"} stroke="#334155" strokeWidth={0.6} />
              </>
            ) : (
              <>
                {/* Bezel */}
                <rect x={elX - bezelW / 2} y={elY - bezelH / 2} width={bezelW} height={bezelH} fill="#e2e8f0" stroke="#475569" strokeWidth={0.8} rx={1} />
                {/* Cutout */}
                <rect x={elX - elW / 2} y={elY - elH / 2} width={elW} height={elH} fill="#f1f5f9" stroke="#334155" strokeWidth={0.6} rx={1} />
              </>
            )}
            {/* Label */}
            <text x={elX} y={elY + bezelH / 2 + 10} textAnchor="middle" fontSize="7" fill="#475569" fontFamily="'Helvetica Neue', sans-serif">
              {spec.name}
            </text>
          </g>
        );
      })}

      {/* Title */}
      <text x={canvasSize / 2} y={canvasSize - 10} textAnchor="middle" fontSize="10" fill="#334155" fontWeight="600" fontFamily="'Helvetica Neue', sans-serif">
        Kapak Düzeni — {box.name}
      </text>
    </svg>
  );
}
