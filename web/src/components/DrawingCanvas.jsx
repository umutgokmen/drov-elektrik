import React from 'react';

const HDim = ({ x1, x2, y, value, below = true }) => {
    const dy = below ? y + 18 : y - 18;
    const mid = (x1 + x2) / 2;
    return (
        <g>
            <line x1={x1} y1={y} x2={x1} y2={dy} stroke="#333" strokeWidth="0.4" />
            <line x1={x2} y1={y} x2={x2} y2={dy} stroke="#333" strokeWidth="0.4" />
            <line x1={x1} y1={dy} x2={x2} y2={dy} stroke="#333" strokeWidth="0.5" />
            <polygon points={`${x1},${dy} ${x1 + 4},${dy - 1.5} ${x1 + 4},${dy + 1.5}`} fill="#333" />
            <polygon points={`${x2},${dy} ${x2 - 4},${dy - 1.5} ${x2 - 4},${dy + 1.5}`} fill="#333" />
            <rect x={mid - 16} y={dy - 6} width={32} height={12} fill="white" />
            <text x={mid} y={dy + 3} textAnchor="middle" fontSize="8" fontFamily="Helvetica, sans-serif" fill="#333">{value}</text>
        </g>
    );
};

const VDim = ({ y1, y2, x, value, right = true }) => {
    const dx = right ? x + 18 : x - 18;
    const mid = (y1 + y2) / 2;
    return (
        <g>
            <line x1={x} y1={y1} x2={dx} y2={y1} stroke="#333" strokeWidth="0.4" />
            <line x1={x} y1={y2} x2={dx} y2={y2} stroke="#333" strokeWidth="0.4" />
            <line x1={dx} y1={y1} x2={dx} y2={y2} stroke="#333" strokeWidth="0.5" />
            <polygon points={`${dx},${y1} ${dx - 1.5},${y1 + 4} ${dx + 1.5},${y1 + 4}`} fill="#333" />
            <polygon points={`${dx},${y2} ${dx - 1.5},${y2 - 4} ${dx + 1.5},${y2 - 4}`} fill="#333" />
            <rect x={dx - 6} y={mid - 16} width={12} height={32} fill="white" />
            <text x={dx} y={mid} textAnchor="middle" fontSize="8" fontFamily="Helvetica, sans-serif" fill="#333" transform={`rotate(-90, ${dx}, ${mid})`}>{value}</text>
        </g>
    );
};

const DrawingCanvas = ({ box, config }) => {
    const canvasWidth = 780;
    const canvasHeight = 560;
    const margin = 30;

    // Box dimensions in mm
    const W = box.internalWidth;   // width
    const L = box.internalLength;  // length (depth in top view)
    const D = box.internalDepth;   // depth (height in front view)

    // Compute unified scale to fit all 3 views
    const gapPx = 60;
    const availW = canvasWidth - 2 * margin - gapPx;
    const availH = canvasHeight - 2 * margin - gapPx - 50; // 50 for header

    const scaleX = availW / (W + L);
    const scaleY = availH / (D + L);
    const s = Math.min(scaleX, scaleY) * 0.82;

    // Front view dimensions in px
    const fW = W * s;
    const fH = D * s;
    // Top view dimensions
    const tW = W * s;
    const tH = L * s;
    // Right view dimensions
    const rW = L * s;
    const rH = D * s;

    // Front view origin (bottom-left of the front view)
    const frontX = margin + 20;
    const frontY = margin + 80; // leave room above for top view label

    // Top view: above front view
    const topX = frontX;
    const topY = frontY + fH + gapPx;

    // Right view: right of front view
    const rightX = frontX + fW + gapPx;
    const rightY = frontY;

    const wallPx = 3 * s;

    // Hole position calculator
    const calcHolePos = (count, sideLen) => {
        if (count <= 0) return [];
        const edgeMar = 15;
        const avail = sideLen - 2 * edgeMar;
        const spacing = avail / (count + 1);
        return Array.from({ length: count }, (_, i) => edgeMar + (i + 1) * spacing);
    };

    // Rail positions
    const railCount = box.railCount || 1;
    const railMargin = 30;
    const railSpacing = railCount > 1 ? (L - 2 * railMargin) / (railCount - 1) : 0;
    const terminalsPerRail = Math.ceil(config.terminals / railCount);
    const termW = 5.2 * s;
    const termH = 10 * s;

    const holeR = 4;

    const holesTop = calcHolePos(config.holesTop, W);
    const holesBottom = calcHolePos(config.holesBottom, W);
    const holesLeft = calcHolePos(config.holesLeft, L);
    const holesRight = calcHolePos(config.holesRight, L);

    // Hole circle component
    const HoleCircle = ({ cx, cy }) => (
        <g>
            <circle cx={cx} cy={cy} r={holeR} fill="none" stroke="#1e293b" strokeWidth="1.2" />
            <line x1={cx - 2.5} y1={cy} x2={cx + 2.5} y2={cy} stroke="#1e293b" strokeWidth="0.5" />
            <line x1={cx} y1={cy - 2.5} x2={cx} y2={cy + 2.5} stroke="#1e293b" strokeWidth="0.5" />
        </g>
    );

    return (
        <svg width={canvasWidth} height={canvasHeight} style={{ background: '#ffffff' }}>
            <defs>
                <pattern id="grid-fine" width="10" height="10" patternUnits="userSpaceOnUse">
                    <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#f5f5f5" strokeWidth="0.3" />
                </pattern>
            </defs>

            <rect x="0" y="0" width={canvasWidth} height={canvasHeight} fill="url(#grid-fine)" />

            {/* Title */}
            <text x={canvasWidth / 2} y="20" textAnchor="middle" fontSize="12" fontWeight="600" fontFamily="Helvetica, sans-serif" fill="#1e293b">
                {box.name} - 3rd Angle Projection
            </text>
            <text x={canvasWidth / 2} y="35" textAnchor="middle" fontSize="9" fontFamily="Helvetica, sans-serif" fill="#64748b">
                Scale ~1:2 | All dimensions in mm
            </text>

            {/* ===== FRONT VIEW (Width x Depth) ===== */}
            <g>
                {/* Outline */}
                <rect x={frontX} y={frontY} width={fW} height={fH}
                    fill="none" stroke="#1e293b" strokeWidth="1.5" />
                {/* Inner cavity */}
                <rect x={frontX + wallPx} y={frontY + wallPx} width={fW - 2 * wallPx} height={fH - 2 * wallPx}
                    fill="none" stroke="#94a3b8" strokeWidth="0.4" strokeDasharray="3,2" />

                {/* Top holes on front view (at top edge) */}
                {holesTop.map((pos, i) => (
                    <HoleCircle key={`ft-${i}`} cx={frontX + pos * s} cy={frontY + fH} />
                ))}
                {/* Bottom holes on front view (at bottom edge) */}
                {holesBottom.map((pos, i) => (
                    <HoleCircle key={`fb-${i}`} cx={frontX + pos * s} cy={frontY} />
                ))}

                {/* Section line A-A */}
                <line x1={frontX - 10} y1={frontY + fH / 2} x2={frontX + fW + 10} y2={frontY + fH / 2}
                    stroke="#1e293b" strokeWidth="0.8" strokeDasharray="8,3,2,3" />
                <text x={frontX - 16} y={frontY + fH / 2 + 4} fontSize="10" fontWeight="600" fill="#1e293b">A</text>
                <text x={frontX + fW + 14} y={frontY + fH / 2 + 4} fontSize="10" fontWeight="600" fill="#1e293b">A</text>

                {/* Dimensions */}
                <HDim x1={frontX} x2={frontX + fW} y={frontY} value={W} below={false} />
                <VDim y1={frontY} y2={frontY + fH} x={frontX + fW} value={D} />

                <text x={frontX + fW / 2} y={frontY - 28} textAnchor="middle" fontSize="10" fontWeight="600" fontFamily="Helvetica, sans-serif" fill="#1e293b">
                    FRONT VIEW
                </text>
            </g>

            {/* ===== TOP VIEW (Width x Length) - above front ===== */}
            <g>
                <rect x={topX} y={topY} width={tW} height={tH}
                    fill="none" stroke="#1e293b" strokeWidth="1.5" />
                <rect x={topX + wallPx} y={topY + wallPx} width={tW - 2 * wallPx} height={tH - 2 * wallPx}
                    fill="none" stroke="#94a3b8" strokeWidth="0.4" strokeDasharray="3,2" />

                {/* DIN Rails */}
                {Array.from({ length: railCount }).map((_, i) => {
                    const railY = railCount > 1
                        ? topY + (railMargin + i * railSpacing) * s
                        : topY + tH / 2;
                    const railW = tW - 40 * s;
                    const railX = topX + 20 * s;
                    return (
                        <g key={`rail-${i}`}>
                            <rect x={railX} y={railY - 3 * s} width={railW} height={6 * s}
                                fill="none" stroke="#94a3b8" strokeWidth="0.75" />
                            <text x={topX + 6} y={railY + 3} fontSize="7" fill="#94a3b8">R{i + 1}</text>
                            {Array.from({ length: Math.min(terminalsPerRail, config.terminals - i * terminalsPerRail) }).map((_, t) => {
                                if (i * terminalsPerRail + t >= config.terminals) return null;
                                const tx = railX + 3 * s + t * (termW + 0.5 * s);
                                if (tx + termW > railX + railW - 3 * s) return null;
                                return (
                                    <rect key={`t-${i}-${t}`}
                                        x={tx} y={railY - termH / 2}
                                        width={termW} height={termH}
                                        fill="none" stroke="#64748b" strokeWidth="0.3" />
                                );
                            })}
                        </g>
                    );
                })}

                {/* Left/Right holes */}
                {holesLeft.map((pos, i) => (
                    <HoleCircle key={`tl-${i}`} cx={topX} cy={topY + pos * s} />
                ))}
                {holesRight.map((pos, i) => (
                    <HoleCircle key={`tr-${i}`} cx={topX + tW} cy={topY + pos * s} />
                ))}

                {/* Section line B-B */}
                <line x1={topX + tW / 2} y1={topY - 8} x2={topX + tW / 2} y2={topY + tH + 8}
                    stroke="#1e293b" strokeWidth="0.8" strokeDasharray="8,3,2,3" />
                <text x={topX + tW / 2} y={topY - 12} textAnchor="middle" fontSize="10" fontWeight="600" fill="#1e293b">B</text>
                <text x={topX + tW / 2} y={topY + tH + 18} textAnchor="middle" fontSize="10" fontWeight="600" fill="#1e293b">B</text>

                <VDim y1={topY} y2={topY + tH} x={topX} value={L} right={false} />

                <text x={topX + tW / 2} y={topY + tH + 30} textAnchor="middle" fontSize="10" fontWeight="600" fontFamily="Helvetica, sans-serif" fill="#1e293b">
                    TOP VIEW
                </text>
            </g>

            {/* ===== RIGHT VIEW (Length x Depth) - right of front ===== */}
            <g>
                <rect x={rightX} y={rightY} width={rW} height={rH}
                    fill="none" stroke="#1e293b" strokeWidth="1.5" />
                <rect x={rightX + wallPx} y={rightY + wallPx} width={rW - 2 * wallPx} height={rH - 2 * wallPx}
                    fill="none" stroke="#94a3b8" strokeWidth="0.4" strokeDasharray="3,2" />

                {/* Right side holes */}
                {holesRight.map((pos, i) => (
                    <HoleCircle key={`rr-${i}`} cx={rightX + pos * s} cy={rightY + rH / 2} />
                ))}

                {/* Rails as hidden lines */}
                {Array.from({ length: railCount }).map((_, i) => {
                    const railY = railCount > 1
                        ? rightY + (railMargin + i * railSpacing) * s * (rH / tH)
                        : rightY + rH * 0.6;
                    return (
                        <line key={`rrl-${i}`}
                            x1={rightX + wallPx} y1={railY}
                            x2={rightX + rW - wallPx} y2={railY}
                            stroke="#94a3b8" strokeWidth="0.4" strokeDasharray="2,2" />
                    );
                })}

                <HDim x1={rightX} x2={rightX + rW} y={rightY} value={L} below={false} />
                <VDim y1={rightY} y2={rightY + rH} x={rightX + rW} value={D} />

                <text x={rightX + rW / 2} y={rightY - 28} textAnchor="middle" fontSize="10" fontWeight="600" fontFamily="Helvetica, sans-serif" fill="#1e293b">
                    RIGHT VIEW
                </text>
            </g>

            {/* Legend */}
            <g transform={`translate(${canvasWidth - 180}, ${canvasHeight - 50})`}>
                <rect x="0" y="0" width="160" height="42" fill="#fafafa" stroke="#e2e8f0" strokeWidth="0.5" rx="3" />
                <circle cx="14" cy="12" r="4" fill="none" stroke="#1e293b" strokeWidth="1" />
                <line x1="12" y1="12" x2="16" y2="12" stroke="#1e293b" strokeWidth="0.5" />
                <line x1="14" y1="10" x2="14" y2="14" stroke="#1e293b" strokeWidth="0.5" />
                <text x="24" y="15" fontSize="8" fill="#475569" fontFamily="Helvetica, sans-serif">Cable Entry Hole</text>
                <rect x="8" y="24" width="12" height="7" fill="none" stroke="#64748b" strokeWidth="0.5" />
                <text x="24" y="31" fontSize="8" fill="#475569" fontFamily="Helvetica, sans-serif">Terminal Block</text>
                <rect x="90" y="8" width="18" height="5" fill="none" stroke="#94a3b8" strokeWidth="0.75" />
                <text x="112" y="15" fontSize="8" fill="#475569" fontFamily="Helvetica, sans-serif">DIN Rail</text>
            </g>

            {/* Drawing number */}
            <text x={margin} y={canvasHeight - 10} fontSize="8" fill="#94a3b8" fontFamily="Helvetica, sans-serif">
                DRV-{box.id?.toUpperCase() || 'XXX'}-001 | Sheet 1/4
            </text>
        </svg>
    );
};

export default DrawingCanvas;
