/**
 * Validation utilities for Drov Engineering Configurator
 * Includes collision detection and distance rule enforcement
 */

import { COMPONENTS } from '../data/constants';

const HOLE_DIAMETER = COMPONENTS.HOLE_M20.diameter;
const MIN_HOLE_CLEARANCE = COMPONENTS.HOLE_M20.clearance;
const MIN_EDGE_MARGIN = 15; // 15mm from box edge

/**
 * Validates if the requested number of holes can physically fit on a side
 * @returns {{ valid: boolean, message: string, maxPossible: number }}
 */
export const validateHolePlacement = (holeCount, sideLength) => {
    if (holeCount === 0) {
        return { valid: true, message: '', maxPossible: 0 };
    }

    const availableLength = sideLength - (2 * MIN_EDGE_MARGIN);
    const spacePerHole = HOLE_DIAMETER + MIN_HOLE_CLEARANCE;
    const maxPossible = Math.floor((availableLength + MIN_HOLE_CLEARANCE) / spacePerHole);

    if (holeCount > maxPossible) {
        return {
            valid: false,
            message: `Fiziksel olarak en fazla ${maxPossible} adet M20 delik sığar. (Kenar: ${sideLength}mm)`,
            maxPossible
        };
    }

    return { valid: true, message: '', maxPossible };
};

/**
 * Validates terminal count against rail capacity
 */
export const validateTerminalPlacement = (terminalCount, box) => {
    const terminalWidth = COMPONENTS.TERMINAL_2_5.width;
    const railMargin = 20; // 20mm from each side of the rail
    const availableRailLength = box.internalWidth - (2 * railMargin);
    const maxPerRail = Math.floor(availableRailLength / terminalWidth);
    const maxTotal = maxPerRail * box.railCount;

    if (terminalCount > maxTotal) {
        return {
            valid: false,
            message: `Ray kapasitesi aşıldı. Fiziksel maksimum: ${maxTotal} klemens.`,
            maxPossible: maxTotal
        };
    }

    if (terminalCount > box.maxTerminals) {
        return {
            valid: false,
            message: `Kutu kapasitesi aşıldı. Maksimum: ${box.maxTerminals} klemens.`,
            maxPossible: box.maxTerminals
        };
    }

    return { valid: true, message: '', maxPossible: box.maxTerminals };
};

/**
 * Runs all validations and returns a summary
 */
export const runFullValidation = (box, config) => {
    const errors = [];
    const warnings = [];

    // Hole validations
    const topValidation = validateHolePlacement(config.holesTop, box.internalWidth);
    const bottomValidation = validateHolePlacement(config.holesBottom, box.internalWidth);
    const leftValidation = validateHolePlacement(config.holesLeft, box.internalLength);
    const rightValidation = validateHolePlacement(config.holesRight, box.internalLength);

    if (!topValidation.valid) errors.push({ field: 'holesTop', ...topValidation });
    if (!bottomValidation.valid) errors.push({ field: 'holesBottom', ...bottomValidation });
    if (!leftValidation.valid) errors.push({ field: 'holesLeft', ...leftValidation });
    if (!rightValidation.valid) errors.push({ field: 'holesRight', ...rightValidation });

    // Terminal validation
    const terminalValidation = validateTerminalPlacement(config.terminals, box);
    if (!terminalValidation.valid) errors.push({ field: 'terminals', ...terminalValidation });

    // Capacity warnings (approaching limits)
    if (config.terminals > box.maxTerminals * 0.9 && terminalValidation.valid) {
        warnings.push({ field: 'terminals', message: 'Klemens kapasitesinin %90\'ına yaklaştınız.' });
    }

    const totalHoles = config.holesTop + config.holesBottom + config.holesLeft + config.holesRight;
    const maxTotalHoles = box.maxHolesLong * 2 + box.maxHolesShort * 2;
    if (totalHoles > maxTotalHoles * 0.9) {
        warnings.push({ field: 'holes', message: 'Toplam delik kapasitesinin %90\'ına yaklaştınız.' });
    }

    return { errors, warnings, isValid: errors.length === 0 };
};
