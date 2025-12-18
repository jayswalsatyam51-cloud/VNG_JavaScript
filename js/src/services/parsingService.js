/**
 * Parsing service for VNG files - JavaScript version
 */

const { ParsedFile, MetricValue } = typeof module !== 'undefined' && module.exports
    ? require('../domain/models')
    : window.VNGDomain;

const { ParsingError } = typeof module !== 'undefined' && module.exports
    ? require('../domain/exceptions')
    : window.VNGExceptions;

const { parseVngText } = typeof module !== 'undefined' && module.exports
    ? require('../modules/parser')
    : window.VNGParser;

/**
 * Service for parsing VNG text files
 */
class ParsingService {
    /**
     * Parse a VNG file and return a ParsedFile domain model
     * @param {string} fileName - Name of the file
     * @param {string} fileContent - Raw text content of the file
     * @param {number} sizeBytes - Size of the file in bytes
     * @returns {ParsedFile} ParsedFile domain model
     */
    static parseFile(fileName, fileContent, sizeBytes = 0) {
        try {
            const rawData = parseVngText(fileContent);

            // Convert to domain models
            const parsedData = {};

            for (const [category, metrics] of Object.entries(rawData)) {
                parsedData[category] = {};

                for (const [metric, data] of Object.entries(metrics)) {
                    parsedData[category][metric] = new MetricValue(
                        data.value,
                        data.isFlagged
                    );
                }
            }

            return new ParsedFile(fileName, parsedData, sizeBytes);
        } catch (error) {
            throw new ParsingError(`Failed to parse file ${fileName}: ${error.message}`);
        }
    }

    /**
     * Parse VNG file content to dictionary format (legacy compatibility)
     * @param {string} fileContent - Raw text content of the file
     * @returns {Object} Dictionary with parsed data
     */
    static parseToDict(fileContent) {
        return parseVngText(fileContent);
    }
}

// Export service
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ParsingService };
} else if (typeof window !== 'undefined') {
    window.VNGServices = window.VNGServices || {};
    window.VNGServices.ParsingService = ParsingService;
}
