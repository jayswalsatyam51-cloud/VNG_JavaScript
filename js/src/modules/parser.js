/**
 * VNG text file parsing module - JavaScript version
 * Converts raw VNG report text into structured data
 */

/**
 * Parses the raw text of a VNG file into a structured dictionary.
 * @param {string} text - The raw text content of the .txt file
 * @returns {Object} A nested dictionary where:
 *                   - Outer key: category name (e.g., "Saccades")
 *                   - Inner key: metric name (e.g., "Latency")
 *                   - Value: object with 'value' (number) and 'isFlagged' (boolean)
 */
function parseVngText(text) {
    const dataMap = {};
    let currentCategory = "General";

    if (!text || typeof text !== 'string') {
        return dataMap;
    }

    const lines = text.split('\n');

    // Regex pattern to match: "Metric Name: 123.45 | FLAG" or "Metric Name: 123.45"
    const valueRegex = /: ([\d.-]+)[\s%a-zA-Z]*?(\| FLAG)?$/;

    for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) {
            continue;
        }

        const match = valueRegex.exec(trimmedLine);

        if (match && match[1]) {
            let value;
            try {
                value = parseFloat(match[1]);
                if (isNaN(value)) {
                    continue;
                }
            } catch (e) {
                continue;
            }

            // Check if the flag exists
            const isFlagged = match[2] !== undefined;

            // Extract metric name (everything before the colon, minus any trailing parentheses)
            const colonIndex = trimmedLine.indexOf(':');
            if (colonIndex === -1) {
                continue;
            }

            let metricName = trimmedLine.substring(0, colonIndex).trim();
            // Remove trailing parentheses and their contents
            metricName = metricName.replace(/\s*\([^)]+\)$/, '').trim();

            // Ensure category exists in dataMap
            if (!(currentCategory in dataMap)) {
                dataMap[currentCategory] = {};
            }

            // Store the metric data
            dataMap[currentCategory][metricName] = {
                'value': value,
                'isFlagged': isFlagged
            };

        } else if (trimmedLine.endsWith(':') && !valueRegex.test(trimmedLine)) {
            // This line is a new category (ends with colon and doesn't match value pattern)
            if (!trimmedLine.includes('Summary of Flagged Findings')) {
                currentCategory = trimmedLine.slice(0, -1).trim();
                // Handle section headers like "VISUOMOTOR //"
                if (currentCategory.endsWith(' //')) {
                    currentCategory = currentCategory.slice(0, -3).trim();
                }
            }
        }
    }

    return dataMap;
}

// Export function
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { parseVngText };
} else if (typeof window !== 'undefined') {
    window.VNGParser = { parseVngText };
}
