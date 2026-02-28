/**
 * Geometry and Layout calculations for Drov
 */

/**
 * Calculates evenly spaced positions for holes on a side
 */
export const calculateHolePositions = (count, sideLength, holeDiameter, _minClearance) => {
    if (count <= 0) return [];

    const totalInternalSpace = sideLength - (2 * (holeDiameter / 2 + 10)); // 10mm margin from corners
    const spacing = totalInternalSpace / (count + 1);

    return Array.from({ length: count }, (_, i) => ({
        pos: (i + 1) * spacing + 10 + holeDiameter / 2
    }));
};

/**
 * Calculates terminal and rail layout
 */
export const calculateLayout = (box, terminalCount, _terminalWidth) => {
    const rails = [];
    const terminalsPerRail = Math.ceil(terminalCount / box.railCount);

    // Calculate rail vertical positions (distributed vertically)
    const verticalMargin = 30; // 30mm from top/bottom
    const availableHeight = box.internalLength - (2 * verticalMargin);
    const railSpacing = box.railCount > 1 ? availableHeight / (box.railCount - 1) : 0;

    for (let i = 0; i < box.railCount; i++) {
        const y = box.railCount > 1
            ? verticalMargin + i * railSpacing
            : box.internalLength / 2;

        const countOnThisRail = i === box.railCount - 1
            ? terminalCount - (i * terminalsPerRail)
            : terminalsPerRail;

        rails.push({
            id: `rail-${i}`,
            y: y,
            terminalCount: countOnThisRail,
            width: box.internalWidth - 40, // 20mm margin from sides
            x: 20
        });
    }

    return rails;
};
