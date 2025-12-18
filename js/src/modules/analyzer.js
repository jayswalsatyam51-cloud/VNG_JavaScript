/**
 * Statistical analysis module for VNG data - JavaScript version
 * Compares metrics across multiple files and calculates statistics
 */

const { calculateStdDev, calculatePercentChange } = typeof module !== 'undefined' && module.exports
    ? require('../utils/statistics')
    : window.VNGStatistics;

/**
 * Analyzes the data from multiple file maps.
 * @param {Array} fileDataList - List of dictionaries, each containing parsed file data
 *                             Format: [{'name': string, 'data': {category: {metric: {value, isFlagged}}}}]
 * @returns {Object} Nested dictionary with analysis results:
 *                   {category: {metric: {values: [], flags: [], delta: number|null,
 *                              stdDev: number|null, percentChange: number|null}}}
 */
function runAnalysis(fileDataList) {
    const results = {};

    if (!Array.isArray(fileDataList) || fileDataList.length === 0) {
        return results;
    }

    const firstMap = fileDataList[0]['data'];

    // 1. Find common category:metric pairs ("Apples to Apples")
    // Build a set of all (category, metric) pairs from the first file
    const commonPairs = new Set();

    for (const category in firstMap) {
        for (const metric in firstMap[category]) {
            commonPairs.add(`${category}::${metric}`);
        }
    }

    // Check which pairs exist in all files
    for (let i = 1; i < fileDataList.length; i++) {
        const fileData = fileDataList[i];
        const filePairs = new Set();

        for (const category in fileData['data']) {
            for (const metric in fileData['data'][category]) {
                filePairs.add(`${category}::${metric}`);
            }
        }

        // Keep only pairs that exist in this file too
        const newCommonPairs = new Set();
        for (const pair of commonPairs) {
            if (filePairs.has(pair)) {
                newCommonPairs.add(pair);
            }
        }
        commonPairs.clear();
        for (const pair of newCommonPairs) {
            commonPairs.add(pair);
        }
    }

    // 2. Populate results and calculate stats
    for (const pair of commonPairs) {
        const [category, metric] = pair.split('::');

        // Extract values and flags separately
        const values = [];
        const flags = [];

        for (const fileData of fileDataList) {
            // Check if category and metric exist in this file
            if (fileData['data'] && fileData['data'][category] && fileData['data'][category][metric]) {
                const metricData = fileData['data'][category][metric];
                values.push(metricData['value']);
                flags.push(metricData['isFlagged']);
            } else {
                // Skip this file if it doesn't have this metric
                continue;
            }
        }

        // Only process if we have data from all files
        if (values.length !== fileDataList.length) {
            continue;
        }

        // Calculate statistics
        let delta = null;
        let stdDev = null;
        let percentChange = null;

        if (fileDataList.length === 2) {
            delta = values[1] - values[0];
            percentChange = calculatePercentChange(values[0], values[1]);
        }

        if (fileDataList.length >= 2) {
            stdDev = calculateStdDev(values);
        }

        // Ensure category exists in results
        if (!(category in results)) {
            results[category] = {};
        }

        // Store metric data
        results[category][metric] = {
            'values': values,
            'flags': flags,
            'delta': delta,
            'stdDev': stdDev,
            'percentChange': percentChange
        };
    }

    return results;
}

// Export function
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runAnalysis };
} else if (typeof window !== 'undefined') {
    window.VNGAnalyzer = { runAnalysis };
}
