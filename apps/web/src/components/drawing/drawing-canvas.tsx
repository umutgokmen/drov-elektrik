"use client";

import type { BoxModel, RailLayout, HolePosition } from "@drov/shared";

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const DIM_COLOR = "#1a1a1a";
const DIM_FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif";
const THIN = 0.35;

/* ------------------------------------------------------------------ */
/*  ISO-style Dimension Components                                     */
/* ------------------------------------------------------------------ */

function HDim({
  x1,
  x2,
  y,
  value,
  below = true,
  offset = 22,
}: {
  x1: number;
  x2: number;
  y: number;
  value: number;
  below?: boolean;
  offset?: number;
}) {
  const dy = below ? y + offset : y - offset;
  const ey1 = below ? y + 3 : y - 3;
  const mid = (x1 + x2) / 2;
  const gap = String(value).length * 3.2 + 6;
  return (
    <g className="dim dim-h">
      <line x1={x1} y1={ey1} x2={x1} y2={dy} stroke={DIM_COLOR} strokeWidth={THIN} />
      <line x1={x2} y1={ey1} x2={x2} y2={dy} stroke={DIM_COLOR} strokeWidth={THIN} />
      <line x1={x1} y1={dy} x2={mid - gap} y2={dy} stroke={DIM_COLOR} strokeWidth={THIN} />
      <line x1={mid + gap} y1={dy} x2={x2} y2={dy} stroke={DIM_COLOR} strokeWidth={THIN} />
      <polygon points={`${x1},${dy} ${x1 + 5},${dy - 1.5} ${x1 + 5},${dy + 1.5}`} fill={DIM_COLOR} />
      <polygon points={`${x2},${dy} ${x2 - 5},${dy - 1.5} ${x2 - 5},${dy + 1.5}`} fill={DIM_COLOR} />
      <text x={mid} y={dy + 3.5} textAnchor="middle" fontSize="9" fontFamily={DIM_FONT} fill={DIM_COLOR} fontWeight="500">
        {value}
      </text>
    </g>
  );
}

function VDim({
  y1,
  y2,
  x,
  value,
  right = true,
  offset = 22,
}: {
  y1: number;
  y2: number;
  x: number;
  value: number;
  right?: boolean;
  offset?: number;
}) {
  const dx = right ? x + offset : x - offset;
  const ex1 = right ? x + 3 : x - 3;
  const mid = (y1 + y2) / 2;
  const gap = String(value).length * 3.2 + 6;
  return (
    <g className="dim dim-v">
      <line x1={ex1} y1={y1} x2={dx} y2={y1} stroke={DIM_COLOR} strokeWidth={THIN} />
      <line x1={ex1} y1={y2} x2={dx} y2={y2} stroke={DIM_COLOR} strokeWidth={THIN} />
      <line x1={dx} y1={y1} x2={dx} y2={mid - gap} stroke={DIM_COLOR} strokeWidth={THIN} />
      <line x1={dx} y1={mid + gap} x2={dx} y2={y2} stroke={DIM_COLOR} strokeWidth={THIN} />
      <polygon points={`${dx},${y1} ${dx - 1.5},${y1 + 5} ${dx + 1.5},${y1 + 5}`} fill={DIM_COLOR} />
      <polygon points={`${dx},${y2} ${dx - 1.5},${y2 - 5} ${dx + 1.5},${y2 - 5}`} fill={DIM_COLOR} />
      <text
        x={dx}
        y={mid}
        textAnchor="middle"
        fontSize="9"
        fontFamily={DIM_FONT}
        fill={DIM_COLOR}
        fontWeight="500"
        transform={`rotate(-90, ${dx}, ${mid})`}
      >
        {value}
      </text>
    </g>
  );
}

/* ------------------------------------------------------------------ */
/*  Hole with center mark (ISO standard)                               */
/* ------------------------------------------------------------------ */

function HoleWithCenter({ cx, cy, r = 5, label }: { cx: number; cy: number; r?: number; label?: string }) {
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1a1a1a" strokeWidth={0.8} />
      <line x1={cx - r - 2} y1={cy} x2={cx - r * 0.4} y2={cy} stroke="#1a1a1a" strokeWidth={THIN} />
      <line x1={cx + r * 0.4} y1={cy} x2={cx + r + 2} y2={cy} stroke="#1a1a1a" strokeWidth={THIN} />
      <line x1={cx} y1={cy - r - 2} x2={cx} y2={cy - r * 0.4} stroke="#1a1a1a" strokeWidth={THIN} />
      <line x1={cx} y1={cy + r * 0.4} x2={cx} y2={cy + r + 2} stroke="#1a1a1a" strokeWidth={THIN} />
      <circle cx={cx} cy={cy} r={0.6} fill="#1a1a1a" />
      {label && (
        <text x={cx} y={cy - r - 5} textAnchor="middle" fontSize="6" fill="#64748b" fontFamily={DIM_FONT}>
          {label}
        </text>
      )}
    </g>
  );
}

/* ------------------------------------------------------------------ */
/*  Section indicator (A-A, B-B)                                       */
/* ------------------------------------------------------------------ */

function SectionLine({
  x1,
  y1,
  x2,
  y2,
  label,
}: {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  label: string;
}) {
  return (
    <g>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#1a1a1a" strokeWidth={0.7} strokeDasharray="12,3,2,3" />
      {y1 === y2 ? (
        <>
          <polygon points={`${x1 - 2},${y1 - 8} ${x1 - 5},${y1 - 14} ${x1 + 1},${y1 - 14}`} fill="#1a1a1a" />
          <text x={x1 - 2} y={y1 - 16} textAnchor="middle" fontSize="11" fontWeight="700" fill="#1a1a1a" fontFamily={DIM_FONT}>
            {label}
          </text>
          <polygon points={`${x2 + 2},${y2 - 8} ${x2 - 1},${y2 - 14} ${x2 + 5},${y2 - 14}`} fill="#1a1a1a" />
          <text x={x2 + 2} y={y2 - 16} textAnchor="middle" fontSize="11" fontWeight="700" fill="#1a1a1a" fontFamily={DIM_FONT}>
            {label}
          </text>
        </>
      ) : (
        <>
          <polygon points={`${x1 + 8},${y1 - 2} ${x1 + 14},${y1 - 5} ${x1 + 14},${y1 + 1}`} fill="#1a1a1a" />
          <text x={x1 + 16} y={y1 + 4} textAnchor="start" fontSize="11" fontWeight="700" fill="#1a1a1a" fontFamily={DIM_FONT}>
            {label}
          </text>
          <polygon points={`${x2 + 8},${y2 + 2} ${x2 + 14},${y2 - 1} ${x2 + 14},${y2 + 5}`} fill="#1a1a1a" />
          <text x={x2 + 16} y={y2 + 4} textAnchor="start" fontSize="11" fontWeight="700" fill="#1a1a1a" fontFamily={DIM_FONT}>
            {label}
          </text>
        </>
      )}
    </g>
  );
}

/* ------------------------------------------------------------------ */
/*  Title Block (ISO 7200 inspired)                                    */
/* ------------------------------------------------------------------ */

function TitleBlock({
  x,
  y,
  boxName,
  boxId,
  date,
  scale = "1:2",
}: {
  x: number;
  y: number;
  boxName: string;
  boxId: string;
  date: string;
  scale?: string;
}) {
  const w = 180;
  const h = 65;
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} fill="#fafcff" stroke="#1a1a1a" strokeWidth={1.2} />
      <line x1={x} y1={y + 18} x2={x + w} y2={y + 18} stroke="#1a1a1a" strokeWidth={0.6} />
      <text x={x + w / 2} y={y + 13} textAnchor="middle" fontSize="11" fontWeight="700" fontFamily={DIM_FONT} fill="#0f172a">
        DROV Engineering
      </text>
      <line x1={x} y1={y + 36} x2={x + w} y2={y + 36} stroke="#1a1a1a" strokeWidth={THIN} />
      <line x1={x + 90} y1={y + 18} x2={x + 90} y2={y + 36} stroke="#1a1a1a" strokeWidth={THIN} />
      <text x={x + 6} y={y + 26} fontSize="6" fill="#64748b" fontFamily={DIM_FONT}>Drawing No.</text>
      <text x={x + 6} y={y + 34} fontSize="9" fontWeight="600" fontFamily={DIM_FONT} fill="#0f172a">
        DRV-{boxId?.toUpperCase()}-001
      </text>
      <text x={x + 96} y={y + 26} fontSize="6" fill="#64748b" fontFamily={DIM_FONT}>Scale</text>
      <text x={x + 96} y={y + 34} fontSize="9" fontWeight="600" fontFamily={DIM_FONT} fill="#0f172a">{scale}</text>
      <line x1={x + 90} y1={y + 36} x2={x + 90} y2={y + h} stroke="#1a1a1a" strokeWidth={THIN} />
      <line x1={x + 135} y1={y + 36} x2={x + 135} y2={y + h} stroke="#1a1a1a" strokeWidth={THIN} />
      <text x={x + 6} y={y + 44} fontSize="6" fill="#64748b" fontFamily={DIM_FONT}>Title</text>
      <text x={x + 6} y={y + 55} fontSize="8" fontWeight="500" fontFamily={DIM_FONT} fill="#0f172a">{boxName}</text>
      <text x={x + 6} y={y + 63} fontSize="7" fill="#64748b" fontFamily={DIM_FONT}>3rd Angle Projection</text>
      <text x={x + 96} y={y + 44} fontSize="6" fill="#64748b" fontFamily={DIM_FONT}>Date</text>
      <text x={x + 96} y={y + 55} fontSize="8" fontFamily={DIM_FONT} fill="#0f172a">{date}</text>
      <text x={x + 141} y={y + 44} fontSize="6" fill="#64748b" fontFamily={DIM_FONT}>Sheet</text>
      <text x={x + 141} y={y + 55} fontSize="8" fontFamily={DIM_FONT} fill="#0f172a">1 / 4</text>
      <g transform={`translate(${x + 150}, ${y + 56})`}>
        <circle cx={0} cy={0} r={3} fill="none" stroke="#1a1a1a" strokeWidth={0.5} />
        <line x1={-5} y1={-4} x2={-5} y2={4} stroke="#1a1a1a" strokeWidth={0.5} />
        <line x1={-5} y1={-4} x2={5} y2={-4} stroke="#1a1a1a" strokeWidth={0.5} />
        <line x1={5} y1={-4} x2={5} y2={4} stroke="#1a1a1a" strokeWidth={0.5} />
      </g>
    </g>
  );
}

/* ------------------------------------------------------------------ */
/*  Main DrawingCanvas Component                                       */
/* ------------------------------------------------------------------ */

interface DrawingCanvasProps {
  box: BoxModel;
  terminals: number;
  holesTop: HolePosition[];
  holesBottom: HolePosition[];
  holesLeft: HolePosition[];
  holesRight: HolePosition[];
  holeSizeTop?: string;
  holeSizeBottom?: string;
  holeSizeLeft?: string;
  holeSizeRight?: string;
  rails: RailLayout[];
}

export function DrawingCanvas({
  box,
  terminals,
  holesTop,
  holesBottom,
  holesLeft,
  holesRight,
  holeSizeTop = "M20",
  holeSizeBottom = "M20",
  holeSizeLeft = "M20",
  holeSizeRight = "M20",
  rails,
}: DrawingCanvasProps) {
  const canvasWidth = 960;
  const canvasHeight = 680;
  const borderMargin = 12;
  const drawingMargin = 50;

  const W = box.internalWidth;
  const L = box.internalLength;
  const D = box.internalDepth;

  const gapPx = 70;
  const availW = canvasWidth - 2 * drawingMargin - gapPx - 200;
  const availH = canvasHeight - 2 * drawingMargin - gapPx - 80;

  const scaleX = availW / (W + L);
  const scaleY = availH / (D + L);
  const s = Math.min(scaleX, scaleY) * 0.78;

  const fW = W * s;
  const fH = D * s;
  const tW = W * s;
  const tH = L * s;
  const rW = L * s;
  const rH = D * s;

  const frontX = drawingMargin + 30;
  const frontY = drawingMargin + 50;
  const topX = frontX;
  const topY = frontY + fH + gapPx;
  const rightX = frontX + fW + gapPx;
  const rightY = frontY;

  const wallThickness = 4;
  const wallPx = wallThickness * s;
  const holeR = 5 * s;

  // Hole positions (use layout positions or calculate)
  const calcHolePos = (count: number, sideLen: number) => {
    if (count <= 0) return [];
    const edgeMar = 20;
    const avail = sideLen - 2 * edgeMar;
    if (count === 1) return [sideLen / 2];
    const spacing = avail / (count - 1);
    return Array.from({ length: count }, (_, i) => edgeMar + i * spacing);
  };

  const htPositions = holesTop.length > 0 ? holesTop.map((h) => h.pos) : calcHolePos(0, W);
  const hbPositions = holesBottom.length > 0 ? holesBottom.map((h) => h.pos) : calcHolePos(0, W);
  const hlPositions = holesLeft.length > 0 ? holesLeft.map((h) => h.pos) : calcHolePos(0, L);
  const hrPositions = holesRight.length > 0 ? holesRight.map((h) => h.pos) : calcHolePos(0, L);

  // Rail positions
  const railCount = box.railCount || 1;
  const railMargin = 35;
  const railSpacing = railCount > 1 ? (L - 2 * railMargin) / (railCount - 1) : 0;
  const terminalsPerRail = Math.ceil(terminals / railCount);
  const termW = 5.2 * s;
  const termH = 10 * s;

  const today = new Date().toLocaleDateString("tr-TR");

  return (
    <svg
      width={canvasWidth}
      height={canvasHeight}
      viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
      style={{ background: "#ffffff" }}
      className="w-full h-auto"
    >
      <defs>
        <pattern id="grid-5" width="5" height="5" patternUnits="userSpaceOnUse">
          <path d="M 5 0 L 0 0 0 5" fill="none" stroke="#f0f4f8" strokeWidth="0.2" />
        </pattern>
        <pattern id="grid-25" width="25" height="25" patternUnits="userSpaceOnUse">
          <rect width="25" height="25" fill="url(#grid-5)" />
          <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#e8edf2" strokeWidth="0.3" />
        </pattern>
        <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="6" stroke="#cbd5e1" strokeWidth="0.4" />
        </pattern>
        <style>{`
          .center-line { stroke-dasharray: 16,3,3,3; }
          .hidden-line { stroke-dasharray: 6,3; }
        `}</style>
      </defs>

      {/* Background grid */}
      <rect
        x={borderMargin}
        y={borderMargin}
        width={canvasWidth - 2 * borderMargin}
        height={canvasHeight - 2 * borderMargin}
        fill="url(#grid-25)"
      />

      {/* Drawing border */}
      <rect
        x={borderMargin}
        y={borderMargin}
        width={canvasWidth - 2 * borderMargin}
        height={canvasHeight - 2 * borderMargin}
        fill="none"
        stroke="#1a1a1a"
        strokeWidth={1.5}
      />

      {/* Zone markers */}
      {["A", "B", "C", "D", "E", "F"].map((letter, i) => {
        const step = (canvasWidth - 2 * borderMargin) / 6;
        const xPos = borderMargin + i * step + step / 2;
        return (
          <g key={`zone-${letter}`}>
            <text x={xPos} y={borderMargin + 8} textAnchor="middle" fontSize="7" fill="#94a3b8" fontFamily={DIM_FONT}>
              {letter}
            </text>
            <text x={xPos} y={canvasHeight - borderMargin - 3} textAnchor="middle" fontSize="7" fill="#94a3b8" fontFamily={DIM_FONT}>
              {letter}
            </text>
          </g>
        );
      })}
      {[1, 2, 3, 4].map((num, i) => {
        const step = (canvasHeight - 2 * borderMargin) / 4;
        const yPos = borderMargin + i * step + step / 2;
        return (
          <g key={`zone-${num}`}>
            <text x={borderMargin + 5} y={yPos + 3} fontSize="7" fill="#94a3b8" fontFamily={DIM_FONT}>
              {num}
            </text>
            <text x={canvasWidth - borderMargin - 5} y={yPos + 3} textAnchor="end" fontSize="7" fill="#94a3b8" fontFamily={DIM_FONT}>
              {num}
            </text>
          </g>
        );
      })}

      {/* ================ FRONT VIEW (Width x Depth) ================ */}
      <g>
        <text x={frontX + fW / 2} y={frontY - 14} textAnchor="middle" fontSize="10" fontWeight="700" fontFamily={DIM_FONT} fill="#0f172a" letterSpacing="0.5">
          FRONT VIEW
        </text>

        <rect x={frontX} y={frontY} width={fW} height={fH} fill="#fafcff" stroke="#0f172a" strokeWidth={1.4} />

        {/* Wall hatching */}
        <rect x={frontX} y={frontY} width={wallPx} height={fH} fill="url(#hatch)" stroke="none" />
        <rect x={frontX + fW - wallPx} y={frontY} width={wallPx} height={fH} fill="url(#hatch)" stroke="none" />
        <rect x={frontX} y={frontY} width={fW} height={wallPx} fill="url(#hatch)" stroke="none" />
        <rect x={frontX + fW - wallPx} y={frontY + fH - wallPx} width={wallPx} height={wallPx} fill="url(#hatch)" stroke="none" />

        {/* Inner cavity */}
        <rect x={frontX + wallPx} y={frontY + wallPx} width={fW - 2 * wallPx} height={fH - 2 * wallPx} fill="none" stroke="#475569" strokeWidth={0.6} />

        {/* Center lines */}
        <line x1={frontX - 8} y1={frontY + fH / 2} x2={frontX + fW + 8} y2={frontY + fH / 2} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />
        <line x1={frontX + fW / 2} y1={frontY - 8} x2={frontX + fW / 2} y2={frontY + fH + 8} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />

        {/* Top holes */}
        {htPositions.map((pos, i) => (
          <HoleWithCenter key={`ft-${i}`} cx={frontX + pos * s} cy={frontY + fH} r={holeR} label={holeSizeTop} />
        ))}
        {/* Bottom holes */}
        {hbPositions.map((pos, i) => (
          <HoleWithCenter key={`fb-${i}`} cx={frontX + pos * s} cy={frontY} r={holeR} label={holeSizeBottom} />
        ))}

        {/* Section line A-A */}
        <SectionLine x1={frontX - 12} y1={frontY + fH / 2} x2={frontX + fW + 12} y2={frontY + fH / 2} label="A" />

        {/* Dimensions */}
        <HDim x1={frontX} x2={frontX + fW} y={frontY} value={W} below={false} offset={28} />
        <VDim y1={frontY} y2={frontY + fH} x={frontX + fW} value={D} offset={28} />
        <HDim x1={frontX} x2={frontX + wallPx} y={frontY + fH} value={wallThickness} offset={14} />
      </g>

      {/* ================ TOP VIEW (Width x Length) ================ */}
      <g>
        <text x={topX + tW / 2} y={topY + tH + 20} textAnchor="middle" fontSize="10" fontWeight="700" fontFamily={DIM_FONT} fill="#0f172a" letterSpacing="0.5">
          TOP VIEW (PLAN)
        </text>

        <rect x={topX} y={topY} width={tW} height={tH} fill="#fafcff" stroke="#0f172a" strokeWidth={1.4} />

        {/* Wall hatching */}
        <rect x={topX} y={topY} width={wallPx} height={tH} fill="url(#hatch)" stroke="none" />
        <rect x={topX + tW - wallPx} y={topY} width={wallPx} height={tH} fill="url(#hatch)" stroke="none" />
        <rect x={topX} y={topY} width={tW} height={wallPx} fill="url(#hatch)" stroke="none" />
        <rect x={topX} y={topY + tH - wallPx} width={tW} height={wallPx} fill="url(#hatch)" stroke="none" />

        {/* Inner cavity */}
        <rect x={topX + wallPx} y={topY + wallPx} width={tW - 2 * wallPx} height={tH - 2 * wallPx} fill="none" stroke="#475569" strokeWidth={0.6} />

        {/* Center lines */}
        <line x1={topX - 8} y1={topY + tH / 2} x2={topX + tW + 8} y2={topY + tH / 2} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />
        <line x1={topX + tW / 2} y1={topY - 8} x2={topX + tW / 2} y2={topY + tH + 8} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />

        {/* DIN Rails with terminals */}
        {Array.from({ length: railCount }).map((_, i) => {
          const railY = railCount > 1 ? topY + (railMargin + i * railSpacing) * s : topY + tH / 2;
          const railW2 = tW - 2 * (25 * s);
          const railX = topX + 25 * s;
          const railH2 = 7 * s;
          const termCount = Math.min(terminalsPerRail, terminals - i * terminalsPerRail);

          return (
            <g key={`rail-${i}`}>
              <rect x={railX} y={railY - railH2 / 2} width={railW2} height={railH2} fill="#f1f5f9" stroke="#64748b" strokeWidth={0.7} />
              <line x1={railX} y1={railY} x2={railX + railW2} y2={railY} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />
              <text x={topX + 8} y={railY + 3} fontSize="7" fill="#64748b" fontFamily={DIM_FONT} fontWeight="600">
                R{i + 1}
              </text>
              {Array.from({ length: Math.max(0, termCount) }).map((_, t) => {
                const tx = railX + 4 * s + t * (termW + 0.6 * s);
                if (tx + termW > railX + railW2 - 4 * s) return null;
                return (
                  <g key={`t-${i}-${t}`}>
                    <rect x={tx} y={railY - termH / 2} width={termW} height={termH} fill="#e2e8f0" stroke="#475569" strokeWidth={0.4} rx={0.5} />
                    <circle cx={tx + termW / 2} cy={railY - termH / 4} r={0.8} fill="#475569" />
                    <circle cx={tx + termW / 2} cy={railY + termH / 4} r={0.8} fill="#475569" />
                  </g>
                );
              })}
            </g>
          );
        })}

        {/* Left holes */}
        {hlPositions.map((pos, i) => (
          <HoleWithCenter key={`tl-${i}`} cx={topX} cy={topY + pos * s} r={holeR} label={holeSizeLeft} />
        ))}
        {/* Right holes */}
        {hrPositions.map((pos, i) => (
          <HoleWithCenter key={`tr-${i}`} cx={topX + tW} cy={topY + pos * s} r={holeR} label={holeSizeRight} />
        ))}

        {/* Section line B-B */}
        <SectionLine x1={topX + tW / 2} y1={topY - 12} x2={topX + tW / 2} y2={topY + tH + 12} label="B" />

        {/* Dimensions */}
        <VDim y1={topY} y2={topY + tH} x={topX} value={L} right={false} offset={28} />
      </g>

      {/* ================ RIGHT VIEW (Length x Depth) ================ */}
      <g>
        <text x={rightX + rW / 2} y={rightY - 14} textAnchor="middle" fontSize="10" fontWeight="700" fontFamily={DIM_FONT} fill="#0f172a" letterSpacing="0.5">
          RIGHT VIEW
        </text>

        <rect x={rightX} y={rightY} width={rW} height={rH} fill="#fafcff" stroke="#0f172a" strokeWidth={1.4} />

        {/* Wall hatching */}
        <rect x={rightX} y={rightY} width={wallPx} height={rH} fill="url(#hatch)" stroke="none" />
        <rect x={rightX + rW - wallPx} y={rightY} width={wallPx} height={rH} fill="url(#hatch)" stroke="none" />
        <rect x={rightX} y={rightY} width={rW} height={wallPx} fill="url(#hatch)" stroke="none" />
        <rect x={rightX} y={rightY + rH - wallPx} width={rW} height={wallPx} fill="url(#hatch)" stroke="none" />

        {/* Inner cavity */}
        <rect x={rightX + wallPx} y={rightY + wallPx} width={rW - 2 * wallPx} height={rH - 2 * wallPx} fill="none" stroke="#475569" strokeWidth={0.6} />

        {/* Center lines */}
        <line x1={rightX - 8} y1={rightY + rH / 2} x2={rightX + rW + 8} y2={rightY + rH / 2} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />
        <line x1={rightX + rW / 2} y1={rightY - 8} x2={rightX + rW / 2} y2={rightY + rH + 8} stroke="#94a3b8" strokeWidth={THIN} className="center-line" />

        {/* Right/Left holes projected */}
        {hrPositions.map((pos, i) => (
          <HoleWithCenter key={`rr-${i}`} cx={rightX + pos * s} cy={rightY + rH} r={holeR} />
        ))}
        {hlPositions.map((pos, i) => (
          <HoleWithCenter key={`rl-${i}`} cx={rightX + pos * s} cy={rightY} r={holeR} />
        ))}

        {/* Rails as hidden lines */}
        {Array.from({ length: railCount }).map((_, i) => {
          const railYNorm = railCount > 1 ? railMargin + i * railSpacing : L / 2;
          const railYPx = rightY + railYNorm * s * (rH / tH);
          return (
            <line
              key={`rrl-${i}`}
              x1={rightX + wallPx + 2}
              y1={railYPx}
              x2={rightX + rW - wallPx - 2}
              y2={railYPx}
              stroke="#94a3b8"
              strokeWidth={0.5}
              className="hidden-line"
            />
          );
        })}

        {/* Dimensions */}
        <HDim x1={rightX} x2={rightX + rW} y={rightY} value={L} below={false} offset={28} />
        <VDim y1={rightY} y2={rightY + rH} x={rightX + rW} value={D} offset={28} />
      </g>

      {/* ================ PROJECTION LINES ================ */}
      <g opacity={0.25}>
        <line x1={frontX} y1={frontY + fH + 5} x2={topX} y2={topY - 5} stroke="#94a3b8" strokeWidth={THIN} strokeDasharray="2,4" />
        <line x1={frontX + fW} y1={frontY + fH + 5} x2={topX + tW} y2={topY - 5} stroke="#94a3b8" strokeWidth={THIN} strokeDasharray="2,4" />
        <line x1={frontX + fW + 5} y1={frontY} x2={rightX - 5} y2={rightY} stroke="#94a3b8" strokeWidth={THIN} strokeDasharray="2,4" />
        <line x1={frontX + fW + 5} y1={frontY + fH} x2={rightX - 5} y2={rightY + rH} stroke="#94a3b8" strokeWidth={THIN} strokeDasharray="2,4" />
      </g>

      {/* ================ LEGEND ================ */}
      <g transform={`translate(${canvasWidth - 200}, ${drawingMargin + 10})`}>
        <rect x="0" y="0" width="170" height="75" fill="#fafcff" stroke="#94a3b8" strokeWidth={THIN} rx="2" />
        <text x="85" y="14" textAnchor="middle" fontSize="8" fontWeight="600" fill="#475569" fontFamily={DIM_FONT}>LEGEND</text>
        <line x1="8" y1="18" x2="162" y2="18" stroke="#e2e8f0" strokeWidth={THIN} />

        <circle cx={22} cy={30} r={5} fill="none" stroke="#1a1a1a" strokeWidth={0.8} />
        <line x1={19} y1={30} x2={25} y2={30} stroke="#1a1a1a" strokeWidth={THIN} />
        <line x1={22} y1={27} x2={22} y2={33} stroke="#1a1a1a" strokeWidth={THIN} />
        <text x="34" y="33" fontSize="8" fill="#475569" fontFamily={DIM_FONT}>Cable Entry (M20/M25/M32)</text>

        <rect x="16" y="42" width="12" height="8" fill="#e2e8f0" stroke="#475569" strokeWidth={0.5} rx={0.5} />
        <text x="34" y="49" fontSize="8" fill="#475569" fontFamily={DIM_FONT}>UT 2,5 Terminal Block</text>

        <rect x="14" y="57" width="16" height="5" fill="#f1f5f9" stroke="#64748b" strokeWidth={0.6} />
        <text x="34" y="63" fontSize="8" fill="#475569" fontFamily={DIM_FONT}>NS 35 DIN Rail</text>
      </g>

      {/* ================ TITLE BLOCK ================ */}
      <TitleBlock x={canvasWidth - 200} y={canvasHeight - borderMargin - 75} boxName={box.name} boxId={box.id} date={today} />

      {/* ================ NOTES ================ */}
      <g>
        <text x={drawingMargin} y={canvasHeight - borderMargin - 8} fontSize="7" fill="#94a3b8" fontFamily={DIM_FONT}>
          ALL DIMENSIONS IN mm | TOLERANCES: ±0.5mm | MATERIAL: GRP (Glass Reinforced Polyester) | PROTECTION: IP66/67
        </text>
      </g>
    </svg>
  );
}
