import React from 'react';

const colors = {
    primary: '#1e3a5f',
    boxFill: '#f8fafc',
    boxStroke: '#1e3a5f',
    railFill: '#64748b',
    holeStroke: '#dc2626',
    text: '#1e293b',
    textLight: '#64748b',
    textMuted: '#94a3b8',
    grid: '#e2e8f0',
};

/**
 * Side View (Yandan Görünüm)
 */
const SideViewCanvas = ({ box, config }) => {
    const scale = 0.5;
    const padding = 60;

    const width = box.internalDepth * scale;
    const height = box.internalLength * scale;
    const canvasWidth = width + padding * 2;
    const canvasHeight = height + padding * 2;

    return (
        <div className="bg-white p-4 rounded-xl border border-gray-200">
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-3 text-center" style={{ color: colors.textLight }}>
                Yandan Görünüm
            </h4>
            <svg
                width={canvasWidth}
                height={canvasHeight}
                viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
                style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
            >
                {/* Dimension */}
                <line x1={padding} y1={padding - 20} x2={padding + width} y2={padding - 20} stroke={colors.textLight} strokeWidth="0.75" />
                <text x={padding + width / 2} y={padding - 25} textAnchor="middle" fontSize="9" fill={colors.text} fontWeight="500">
                    {box.internalDepth}mm
                </text>

                {/* Box Frame */}
                <rect x={padding} y={padding} width={width} height={height} fill={colors.boxFill} stroke={colors.boxStroke} strokeWidth="2" rx="2" />

                {/* Rails */}
                {Array.from({ length: box.railCount }).map((_, i) => {
                    const yPos = padding + (i + 1) * (height / (box.railCount + 1));
                    return (
                        <g key={i}>
                            <line x1={padding + 12} y1={yPos} x2={padding + width - 12} y2={yPos} stroke={colors.railFill} strokeWidth="3" strokeLinecap="round" />
                            <text x={padding + 16} y={yPos - 6} fontSize="7" fill={colors.textMuted}>R{i + 1}</text>
                        </g>
                    );
                })}

                {/* Left holes indicator */}
                {config.holesLeft > 0 && Array.from({ length: Math.min(config.holesLeft, 4) }).map((_, i) => {
                    const yPos = padding + (i + 1) * (height / (config.holesLeft + 1));
                    return <circle key={i} cx={padding - 8} cy={yPos} r={5} fill="none" stroke={colors.holeStroke} strokeDasharray="2,2" />;
                })}
                {config.holesLeft > 4 && (
                    <text x={padding - 8} y={padding + height - 10} textAnchor="middle" fontSize="7" fill={colors.textMuted}>+{config.holesLeft - 4}</text>
                )}
            </svg>
        </div>
    );
};

/**
 * Front View (Önden Görünüm)
 */
const FrontViewCanvas = ({ box, config }) => {
    const scale = 0.5;
    const padding = 60;

    const width = box.internalWidth * scale;
    const height = box.internalDepth * scale;
    const canvasWidth = width + padding * 2;
    const canvasHeight = height + padding * 2;

    return (
        <div className="bg-white p-4 rounded-xl border border-gray-200">
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-3 text-center" style={{ color: colors.textLight }}>
                Önden Görünüm
            </h4>
            <svg
                width={canvasWidth}
                height={canvasHeight}
                viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
                style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
            >
                {/* Dimensions */}
                <line x1={padding} y1={padding - 20} x2={padding + width} y2={padding - 20} stroke={colors.textLight} strokeWidth="0.75" />
                <text x={padding + width / 2} y={padding - 25} textAnchor="middle" fontSize="9" fill={colors.text} fontWeight="500">
                    {box.internalWidth}mm
                </text>

                <line x1={padding - 20} y1={padding} x2={padding - 20} y2={padding + height} stroke={colors.textLight} strokeWidth="0.75" />
                <text x={padding - 25} y={padding + height / 2} textAnchor="middle" fontSize="9" fill={colors.text} fontWeight="500"
                    transform={`rotate(-90, ${padding - 25}, ${padding + height / 2})`}>
                    {box.internalDepth}mm
                </text>

                {/* Box Frame */}
                <rect x={padding} y={padding} width={width} height={height} fill={colors.boxFill} stroke={colors.boxStroke} strokeWidth="2" rx="2" />

                {/* Top holes indicator */}
                {config.holesTop > 0 && Array.from({ length: Math.min(config.holesTop, 5) }).map((_, i) => {
                    const xPos = padding + (i + 1) * (width / (Math.min(config.holesTop, 5) + 1));
                    return <circle key={i} cx={xPos} cy={padding - 8} r={5} fill="none" stroke={colors.holeStroke} strokeDasharray="2,2" />;
                })}
                {config.holesTop > 5 && (
                    <text x={padding + width - 15} y={padding - 5} fontSize="7" fill={colors.textMuted}>+{config.holesTop - 5}</text>
                )}

                {/* Bottom holes indicator */}
                {config.holesBottom > 0 && Array.from({ length: Math.min(config.holesBottom, 5) }).map((_, i) => {
                    const xPos = padding + (i + 1) * (width / (Math.min(config.holesBottom, 5) + 1));
                    return <circle key={i} cx={xPos} cy={padding + height + 8} r={5} fill="none" stroke={colors.holeStroke} strokeDasharray="2,2" />;
                })}
            </svg>
        </div>
    );
};

export { SideViewCanvas, FrontViewCanvas };
