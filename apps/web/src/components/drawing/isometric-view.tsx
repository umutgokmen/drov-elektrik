"use client";

import type { BoxModel } from "@drov/shared";

/* ------------------------------------------------------------------ */
/*  Isometric projection helpers                                       */
/* ------------------------------------------------------------------ */

const ISO_ANGLE = Math.PI / 6; // 30 degrees
const COS30 = Math.cos(ISO_ANGLE);
const SIN30 = Math.sin(ISO_ANGLE);

function iso(x: number, y: number, z: number) {
  return {
    x: (x - y) * COS30,
    y: (x + y) * SIN30 - z,
  };
}

function isoPath(points: { x: number; y: number }[]) {
  return (
    points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(" ") + " Z"
  );
}

/* ------------------------------------------------------------------ */
/*  Colors                                                             */
/* ------------------------------------------------------------------ */

const faceTop = "#e8edf3";
const faceRight = "#c8d0db";
const faceFront = "#dde3ec";
const innerColor = "#f5f7fa";
const wallColor = "#b8c4d4";
const edgeColor = "#3b4f6b";
const holeColor = "#2d3748";
const railColor = "#8896a8";

/* ------------------------------------------------------------------ */
/*  Main Component                                                     */
/* ------------------------------------------------------------------ */

interface IsometricViewProps {
  box: BoxModel;
  holesTopCount: number;
  holesBottomCount: number;
  holesLeftCount: number;
  holesRightCount: number;
}

export function IsometricView({
  box,
  holesTopCount,
  holesBottomCount,
  holesLeftCount,
  holesRightCount,
}: IsometricViewProps) {
  const W = box.internalWidth;
  const L = box.internalLength;
  const D = box.internalDepth;

  const maxDim = Math.max(W, L, D);
  const viewSize = 500;
  const s = (viewSize * 0.35) / maxDim;

  const sw = W * s;
  const sl = L * s;
  const sd = D * s;
  const wall = 4 * s;

  const cx = viewSize / 2;
  const cy = viewSize / 2 + sd * 0.15;

  function p(x: number, y: number, z: number) {
    const i = iso(x, y, z);
    return { x: cx + i.x, y: cy + i.y };
  }

  // Box corners
  const corners = {
    b0: p(0, 0, 0),
    b1: p(sw, 0, 0),
    b2: p(sw, sl, 0),
    b3: p(0, sl, 0),
    t0: p(0, 0, sd),
    t1: p(sw, 0, sd),
    t2: p(sw, sl, sd),
    t3: p(0, sl, sd),
  };

  // Inner cavity
  const inner = {
    b0: p(wall, wall, wall),
    b1: p(sw - wall, wall, wall),
    b2: p(sw - wall, sl - wall, wall),
    b3: p(wall, sl - wall, wall),
    t0: p(wall, wall, sd),
    t1: p(sw - wall, wall, sd),
    t2: p(sw - wall, sl - wall, sd),
    t3: p(wall, sl - wall, sd),
  };

  // Hole positions
  const calcHolePos = (count: number, sideLen: number) => {
    if (count <= 0) return [];
    const edgeMar = 20 * s;
    const avail = sideLen - 2 * edgeMar;
    if (count === 1) return [sideLen / 2];
    const spacing = avail / (count - 1);
    return Array.from({ length: count }, (_, i) => edgeMar + i * spacing);
  };

  const htPos = calcHolePos(holesTopCount, sw);
  const hbPos = calcHolePos(holesBottomCount, sw);
  const hlPos = calcHolePos(holesLeftCount, sl);
  const hrPos = calcHolePos(holesRightCount, sl);
  const holeR = 4 * s;

  // DIN Rails
  const railCount = box.railCount || 1;
  const railMarginMm = 35;
  const railSpacingMm = railCount > 1 ? (L - 2 * railMarginMm) / (railCount - 1) : 0;

  return (
    <svg
      width="100%"
      height="100%"
      viewBox={`0 0 ${viewSize} ${viewSize}`}
      style={{ background: "transparent" }}
    >
      {/* Back faces (drawn first) */}
      <path d={isoPath([corners.b0, corners.b1, corners.b2, corners.b3])} fill={faceTop} stroke={edgeColor} strokeWidth={0.8} opacity={0.3} />
      <path d={isoPath([corners.b3, corners.b2, corners.t2, corners.t3])} fill={faceRight} stroke={edgeColor} strokeWidth={0.5} opacity={0.2} />
      <path d={isoPath([corners.b1, corners.b2, corners.t2, corners.t1])} fill={faceFront} stroke={edgeColor} strokeWidth={0.5} opacity={0.2} />

      {/* Front face (y=0) */}
      <path d={isoPath([corners.b0, corners.b1, corners.t1, corners.t0])} fill={faceFront} stroke={edgeColor} strokeWidth={1} />

      {/* Left face (x=0) */}
      <path d={isoPath([corners.b0, corners.b3, corners.t3, corners.t0])} fill={faceRight} stroke={edgeColor} strokeWidth={1} />

      {/* Top face - outer rim */}
      <path d={isoPath([corners.t0, corners.t1, corners.t2, corners.t3])} fill={faceTop} stroke={edgeColor} strokeWidth={1} />

      {/* Top face - inner opening */}
      <path d={isoPath([inner.t0, inner.t1, inner.t2, inner.t3])} fill={innerColor} stroke={edgeColor} strokeWidth={0.6} />

      {/* Inner walls visible from top */}
      <path d={isoPath([inner.b0, inner.b1, inner.t1, inner.t0])} fill={wallColor} stroke={edgeColor} strokeWidth={0.4} opacity={0.6} />
      <path d={isoPath([inner.b0, inner.b3, inner.t3, inner.t0])} fill={wallColor} stroke={edgeColor} strokeWidth={0.4} opacity={0.5} />
      <path d={isoPath([inner.b0, inner.b1, inner.b2, inner.b3])} fill="#eef1f6" stroke={edgeColor} strokeWidth={0.3} opacity={0.7} />

      {/* DIN Rails */}
      {Array.from({ length: railCount }).map((_, i) => {
        const railYmm = railCount > 1 ? railMarginMm + i * railSpacingMm : L / 2;
        const ry = railYmm * s;
        const rx1 = wall + 15 * s;
        const rx2 = sw - wall - 15 * s;
        const railW = 7 * s;
        const rp0 = p(rx1, ry - railW / 2, wall);
        const rp1 = p(rx2, ry - railW / 2, wall);
        const rp2 = p(rx2, ry + railW / 2, wall);
        const rp3 = p(rx1, ry + railW / 2, wall);
        return <path key={`rail-${i}`} d={isoPath([rp0, rp1, rp2, rp3])} fill="#d4dae3" stroke={railColor} strokeWidth={0.6} />;
      })}

      {/* Holes on front face (top side) */}
      {htPos.map((hx, i) => {
        const hCenter = p(hx, 0, sd / 2);
        return (
          <ellipse key={`ht-${i}`} cx={hCenter.x} cy={hCenter.y} rx={holeR * COS30} ry={holeR * 0.55} fill="#4a5568" stroke={holeColor} strokeWidth={0.6} opacity={0.8} />
        );
      })}

      {/* Bottom holes on front face */}
      {hbPos.map((hx, i) => {
        const hCenter = p(hx, 0, sd / 2);
        return (
          <ellipse key={`hb-${i}`} cx={hCenter.x} cy={hCenter.y + sd * 0.15} rx={holeR * COS30} ry={holeR * 0.55} fill="#4a5568" stroke={holeColor} strokeWidth={0.6} opacity={0.8} />
        );
      })}

      {/* Left holes on left face */}
      {hlPos.map((hy, i) => {
        const hCenter = p(0, hy, sd / 2);
        return (
          <ellipse
            key={`hl-${i}`}
            cx={hCenter.x}
            cy={hCenter.y}
            rx={holeR * COS30}
            ry={holeR * 0.55}
            fill="#4a5568"
            stroke={holeColor}
            strokeWidth={0.6}
            opacity={0.8}
            transform={`rotate(-30, ${hCenter.x}, ${hCenter.y})`}
          />
        );
      })}

      {/* Right holes */}
      {hrPos.map((hy, i) => {
        const hCenter = p(sw, hy, sd / 2);
        return (
          <ellipse
            key={`hr-${i}`}
            cx={hCenter.x}
            cy={hCenter.y}
            rx={holeR * COS30}
            ry={holeR * 0.55}
            fill="#4a5568"
            stroke={holeColor}
            strokeWidth={0.6}
            opacity={0.8}
            transform={`rotate(30, ${hCenter.x}, ${hCenter.y})`}
          />
        );
      })}

      {/* Dimensions */}
      <text x={viewSize / 2} y={viewSize - 20} textAnchor="middle" fontSize="11" fontFamily="'Helvetica Neue', sans-serif" fill="#475569" fontWeight="500">
        {box.name} — {W}x{L}x{D} mm
      </text>
      <text x={viewSize / 2} y={viewSize - 6} textAnchor="middle" fontSize="9" fontFamily="'Helvetica Neue', sans-serif" fill="#94a3b8">
        Isometric Projection (30°)
      </text>
    </svg>
  );
}
