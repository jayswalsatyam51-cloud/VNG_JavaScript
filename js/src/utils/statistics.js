/**
 * Statistical helper functions for VNG data analysis - JavaScript version
 */

/**
 * Calculates the standard deviation of an array of numbers (sample standard deviation).
 * @param {number[]} values - Array of numbers
 * @returns {number} The standard deviation (0 if less than 2 values)
 */
function calculateStdDev(values) {
    if (!Array.isArray(values) || values.length < 2) {
        return 0.0;
    }

    // Filter out null/undefined values
    const validValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));

    if (validValues.length < 2) {
        return 0.0;
    }

    // Calculate mean
    const mean = validValues.reduce((sum, val) => sum + val, 0) / validValues.length;

    // Calculate variance
    const variance = validValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (validValues.length - 1);

    return Math.sqrt(variance);
}

/**
 * Calculates the percent change from baseline to new value.
 * Handles division by zero cases.
 * @param {number} baseline - The baseline value
 * @param {number} newValue - The new value
 * @returns {number|null} The percent change, or null if N/A
 */
function calculatePercentChange(baseline, newValue) {
    if (baseline === null || baseline === undefined ||
        newValue === null || newValue === undefined) {
        return null;
    }

    if (baseline === 0) {
        // 0->0 is 0% change. 0->5 is undefined change
        return newValue === 0 ? 0.0 : null;
    }

    return ((newValue - baseline) / baseline) * 100;
}

/**
 * Calculates a simple linear regression trendline.
 * @param {number[]} yValues - Array of Y-axis values
 * @returns {number[]} Array of Y-values for the trendline
 */
function calculateLinearRegression(yValues) {
    if (!Array.isArray(yValues) || yValues.length < 2) {
        return [];
    }

    const n = yValues.length;

    // Create x values [0, 1, 2, ...]
    const xValues = Array.from({length: n}, (_, i) => i);

    // Filter out null/undefined/NaN values
    const validPoints = [];
    for (let i = 0; i < n; i++) {
        const y = yValues[i];
        if (y !== null && y !== undefined && !isNaN(y)) {
            validPoints.push([xValues[i], y]);
        }
    }

    if (validPoints.length < 2) {
        return Array(n).fill(null);
    }

    // Calculate sums
    let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
    const vn = validPoints.length;

    for (const [x, y] of validPoints) {
        sumX += x;
        sumY += y;
        sumXY += x * y;
        sumXX += x * x;
    }

    // Calculate slope and intercept
    const denominator = vn * sumXX - sumX * sumX;

    let slope, intercept;
    if (denominator === 0) {
        // Vertical line - unlikely but handle it
        slope = 0;
        intercept = sumY / vn;
    } else {
        slope = (vn * sumXY - sumX * sumY) / denominator;
        intercept = (sumY - slope * sumX) / vn;
    }

    // Generate trendline values
    return xValues.map(x => slope * x + intercept);
}

/**
 * Calculates the mean of an array of numbers
 * @param {number[]} values - Array of numbers
 * @returns {number} The mean value
 */
function calculateMean(values) {
    if (!Array.isArray(values) || values.length === 0) {
        return 0;
    }

    const validValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));

    if (validValues.length === 0) {
        return 0;
    }

    return validValues.reduce((sum, val) => sum + val, 0) / validValues.length;
}

/**
 * Calculates the median of an array of numbers
 * @param {number[]} values - Array of numbers
 * @returns {number} The median value
 */
function calculateMedian(values) {
    if (!Array.isArray(values) || values.length === 0) {
        return 0;
    }

    const validValues = values.filter(v => v !== null && v !== undefined && !isNaN(v)).sort((a, b) => a - b);

    if (validValues.length === 0) {
        return 0;
    }

    const mid = Math.floor(validValues.length / 2);

    if (validValues.length % 2 === 0) {
        return (validValues[mid - 1] + validValues[mid]) / 2;
    } else {
        return validValues[mid];
    }
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateStdDev,
        calculatePercentChange,
        calculateLinearRegression,
        calculateMean,
        calculateMedian
    };
} else if (typeof window !== 'undefined') {
    window.VNGStatistics = {
        calculateStdDev,
        calculatePercentChange,
        calculateLinearRegression,
        calculateMean,
        calculateMedian
    };
}
