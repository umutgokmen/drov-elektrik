import React from 'react';

/**
 * Industrial-grade CAD Drawing Canvas
 * Clean, technical drawing style matching professional engineering software
 */
const DrawingCanvas = ({ box, config }) => {
    // A4 landscape proportions for preview
    const canvasWidth = 680;
    const canvasHeight = 480;

    const margin = 40;
    const drawScale = 0.35;

    // Calculate scaled dimensions
    const boxWidth = box.internalWidth * drawScale;
    const boxHeight = box.internalLength * drawScale;

    // Drawing area position (centered)
    const drawX = (canvasWidth - boxWidth) / 2;
    const drawY = 120;

    // Calculate hole positions
    const calculateHolePositions = (count, sideLength) => {
        if (count <= 0) return [];
        const edgeMargin = 15;
        const available = sideLength - (2 * edgeMargin);
        const spacing = available / (count + 1);
        return Array.from({ length: count }, (_, i) => edgeMargin + (i + 1) * spacing);
    };

    const holesTop = calculateHolePositions(config.holesTop, box.internalWidth);
    const holesBottom = calculateHolePositions(config.holesBottom, box.internalWidth);
    const holesLeft = calculateHolePositions(config.holesLeft, box.internalLength);
    const holesRight = calculateHolePositions(config.holesRight, box.internalLength);

    // Calculate rail positions
    const railMargin = 30;
    const railCount = box.railCount || 1;
    const railSpacing = railCount > 1 ? (box.internalLength - 2 * railMargin) / (railCount - 1) : 0;
    const terminalsPerRail = Math.ceil(config.terminals / railCount);

    const holeRadius = 4;
    const terminalWidth = 5.2 * drawScale;
    const terminalHeight = 47 * drawScale;

    return (
        <svg
            width={canvasWidth}
            height={canvasHeight}
            style={{ background: '#ffffff' }}
        >
            <defs>
                {/* Grid pattern */}
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" strokeWidth="0.5" />
                </pattern>
                {/* Hatch pattern for section view */}
                <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                    <line x1="0" y1="0" x2="0" y2="6" stroke="#cbd5e1" strokeWidth="0.5" />
                </pattern>
            </defs>

            {/* Background grid */}
            <rect x="0" y="0" width={canvasWidth} height={canvasHeight} fill="url(#grid)" />

            {/* Title */}
            <text x={canvasWidth / 2} y="30" textAnchor="middle" fontSize="14" fontWeight="600" fill="#1e293b">
                TOP VIEW - {box.name}
            </text>
            <text x={canvasWidth / 2} y="48" textAnchor="middle" fontSize="10" fill="#64748b">
                Scale 1:2 | All dimensions in mm
            </text>

            {/* Section line A-A */}
            <text x={drawX - 25} y={drawY + boxHeight / 2 + 4} fontSize="12" fontWeight="600" fill="#1e293b">A</text>
            <line
                x1={drawX - 15} y1={drawY + boxHeight / 2}
                x2={drawX - 8} y2={drawY + boxHeight / 2}
                stroke="#1e293b" strokeWidth="2"
            />
            <text x={drawX + boxWidth + 15} y={drawY + boxHeight / 2 + 4} fontSize="12" fontWeight="600" fill="#1e293b">A</text>
            <line
                x1={drawX + boxWidth + 8} y1={drawY + boxHeight / 2}
                x2={drawX + boxWidth + 15} y2={drawY + boxHeight / 2}
                stroke="#1e293b" strokeWidth="2"
            />

            {/* Main enclosure outline */}
            <rect
                x={drawX} y={drawY}
                width={boxWidth} height={boxHeight}
                fill="none"
                stroke="#1e293b"
                strokeWidth="2"
            />

            {/* Inner cavity */}
            <rect
                x={drawX + 4} y={drawY + 4}
                width={boxWidth - 8} height={boxHeight - 8}
                fill="none"
                stroke="#64748b"
                strokeWidth="0.75"
                strokeDasharray="2,2"
            />

            {/* DIN Rails */}
            {Array.from({ length: railCount }).map((_, i) => {
                const railY = railCount > 1
                    ? drawY + (railMargin + i * railSpacing) * drawScale
                    : drawY + boxHeight / 2;
                const railWidth = boxWidth - 40;

                return (
                    <g key={`rail-${i}`}>
                        {/* Rail body */}
                        <rect
                            x={drawX + 20}
                            y={railY - 5}
                            width={railWidth}
                            height={10}
                            fill="#e2e8f0"
                            stroke="#94a3b8"
                            strokeWidth="1"
                        />
                        {/* Rail label */}
                        <text
                            x={drawX + 10}
                            y={railY + 4}
                            fontSize="8"
                            fill="#64748b"
                        >
                            R{i + 1}
                        </text>

                        {/* Terminals on this rail */}
                        {Array.from({ length: Math.min(terminalsPerRail, config.terminals - i * terminalsPerRail) }).map((_, t) => {
                            if (i * terminalsPerRail + t >= config.terminals) return null;
                            return (
                                <rect
                                    key={`term-${i}-${t}`}
                                    x={drawX + 25 + t * (terminalWidth + 1)}
                                    y={railY - terminalHeight / 2}
                                    width={terminalWidth}
                                    height={terminalHeight}
                                    fill="#a3e635"
                                    stroke="#65a30d"
                                    strokeWidth="0.5"
                                    rx="1"
                                />
                            );
                        })}
                    </g>
                );
            })}

            {/* M20 Holes - Top */}
            {holesTop.map((pos, i) => (
                <g key={`hole-top-${i}`}>
                    <circle
                        cx={drawX + pos * drawScale}
                        cy={drawY - 12}
                        r={holeRadius}
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="1.5"
                    />
                    <line
                        x1={drawX + pos * drawScale - 3}
                        y1={drawY - 12}
                        x2={drawX + pos * drawScale + 3}
                        y2={drawY - 12}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                    <line
                        x1={drawX + pos * drawScale}
                        y1={drawY - 15}
                        x2={drawX + pos * drawScale}
                        y2={drawY - 9}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                </g>
            ))}

            {/* M20 Holes - Bottom */}
            {holesBottom.map((pos, i) => (
                <g key={`hole-bottom-${i}`}>
                    <circle
                        cx={drawX + pos * drawScale}
                        cy={drawY + boxHeight + 12}
                        r={holeRadius}
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="1.5"
                    />
                    <line
                        x1={drawX + pos * drawScale - 3}
                        y1={drawY + boxHeight + 12}
                        x2={drawX + pos * drawScale + 3}
                        y2={drawY + boxHeight + 12}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                    <line
                        x1={drawX + pos * drawScale}
                        y1={drawY + boxHeight + 9}
                        x2={drawX + pos * drawScale}
                        y2={drawY + boxHeight + 15}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                </g>
            ))}

            {/* M20 Holes - Left */}
            {holesLeft.map((pos, i) => (
                <g key={`hole-left-${i}`}>
                    <circle
                        cx={drawX - 12}
                        cy={drawY + pos * drawScale}
                        r={holeRadius}
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="1.5"
                    />
                    <line
                        x1={drawX - 15}
                        y1={drawY + pos * drawScale}
                        x2={drawX - 9}
                        y2={drawY + pos * drawScale}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                    <line
                        x1={drawX - 12}
                        y1={drawY + pos * drawScale - 3}
                        x2={drawX - 12}
                        y2={drawY + pos * drawScale + 3}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                </g>
            ))}

            {/* M20 Holes - Right */}
            {holesRight.map((pos, i) => (
                <g key={`hole-right-${i}`}>
                    <circle
                        cx={drawX + boxWidth + 12}
                        cy={drawY + pos * drawScale}
                        r={holeRadius}
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="1.5"
                    />
                    <line
                        x1={drawX + boxWidth + 9}
                        y1={drawY + pos * drawScale}
                        x2={drawX + boxWidth + 15}
                        y2={drawY + pos * drawScale}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                    <line
                        x1={drawX + boxWidth + 12}
                        y1={drawY + pos * drawScale - 3}
                        x2={drawX + boxWidth + 12}
                        y2={drawY + pos * drawScale + 3}
                        stroke="#ef4444"
                        strokeWidth="0.75"
                    />
                </g>
            ))}

            {/* Dimension - Width */}
            <g>
                <line
                    x1={drawX}
                    y1={drawY + boxHeight + 35}
                    x2={drawX + boxWidth}
                    y2={drawY + boxHeight + 35}
                    stroke="#f59e0b"
                    strokeWidth="1"
                    markerEnd="url(#arrow)"
                    markerStart="url(#arrow)"
                />
                <line x1={drawX} y1={drawY + boxHeight + 28} x2={drawX} y2={drawY + boxHeight + 42} stroke="#f59e0b" strokeWidth="0.5" />
                <line x1={drawX + boxWidth} y1={drawY + boxHeight + 28} x2={drawX + boxWidth} y2={drawY + boxHeight + 42} stroke="#f59e0b" strokeWidth="0.5" />
                <rect x={drawX + boxWidth / 2 - 20} y={drawY + boxHeight + 28} width="40" height="14" fill="white" />
                <text x={drawX + boxWidth / 2} y={drawY + boxHeight + 39} textAnchor="middle" fontSize="10" fontWeight="500" fill="#f59e0b">
                    {box.internalWidth}
                </text>
            </g>

            {/* Dimension - Height */}
            <g>
                <line
                    x1={drawX + boxWidth + 35}
                    y1={drawY}
                    x2={drawX + boxWidth + 35}
                    y2={drawY + boxHeight}
                    stroke="#f59e0b"
                    strokeWidth="1"
                />
                <line x1={drawX + boxWidth + 28} y1={drawY} x2={drawX + boxWidth + 42} y2={drawY} stroke="#f59e0b" strokeWidth="0.5" />
                <line x1={drawX + boxWidth + 28} y1={drawY + boxHeight} x2={drawX + boxWidth + 42} y2={drawY + boxHeight} stroke="#f59e0b" strokeWidth="0.5" />
                <rect x={drawX + boxWidth + 28} y={drawY + boxHeight / 2 - 7} width="40" height="14" fill="white" />
                <text x={drawX + boxWidth + 48} y={drawY + boxHeight / 2 + 4} textAnchor="middle" fontSize="10" fontWeight="500" fill="#f59e0b">
                    {box.internalLength}
                </text>
            </g>

            {/* Legend */}
            <g transform={`translate(${margin}, ${canvasHeight - 70})`}>
                <rect x="0" y="0" width="200" height="62" fill="#f8fafc" stroke="#e2e8f0" strokeWidth="1" rx="4" />
                <circle cx="15" cy="12" r="4" fill="none" stroke="#ef4444" strokeWidth="1.5" />
                <text x="25" y="15" fontSize="9" fill="#475569">M20 Cable Entry</text>
                <rect x="8" y="24" width="14" height="8" fill="#a3e635" stroke="#65a30d" strokeWidth="0.5" rx="1" />
                <text x="25" y="31" fontSize="9" fill="#475569">UT 2,5 Terminal</text>
                <rect x="80" y="8" width="20" height="6" fill="#e2e8f0" stroke="#94a3b8" strokeWidth="0.5" />
                <text x="105" y="15" fontSize="9" fill="#475569">DIN Rail</text>
                {/* Salt malzeme components */}
                <circle cx="90" cy="30" r="4" fill="none" stroke="#8b5cf6" strokeWidth="1.5" strokeDasharray="2,1" />
                <text x="100" y="33" fontSize="9" fill="#475569">Drain Valve</text>
                <rect x="85" y="43" width="10" height="6" fill="none" stroke="#f59e0b" strokeWidth="1" />
                <text x="100" y="49" fontSize="9" fill="#475569">End Clamp</text>
                <text x="3" y="58" fontSize="8" fill="#94a3b8" fontStyle="italic">* Drain valve &amp; end clamps: standard items</text>
            </g>

            {/* Drawing number */}
            <text x={canvasWidth - margin} y={canvasHeight - 15} textAnchor="end" fontSize="9" fill="#94a3b8">
                DRV-{box.id?.toUpperCase() || 'XXX'}-001 | Sheet 1/1
            </text>
        </svg>
    );
};

export default DrawingCanvas;
