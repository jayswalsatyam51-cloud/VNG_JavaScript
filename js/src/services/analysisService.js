/**
 * Analysis service for VNG data - JavaScript version
 */

const { ParsedFile, AnalysisResult, AnalysisResults, MetricData } = typeof module !== 'undefined' && module.exports
    ? require('../domain/models')
    : window.VNGDomain;

const { AnalysisError } = typeof module !== 'undefined' && module.exports
    ? require('../domain/exceptions')
    : window.VNGExceptions;

const { runAnalysis } = typeof module !== 'undefined' && module.exports
    ? require('../modules/analyzer')
    : window.VNGAnalyzer;

/**
 * Service for analyzing VNG data
 */
class AnalysisService {
    /**
     * Analyze multiple parsed files and return AnalysisResults
     * @param {ParsedFile[]} parsedFiles - List of ParsedFile domain models
     * @returns {AnalysisResults} AnalysisResults domain model
     */
    static analyzeFiles(parsedFiles) {
        try {
            if (!Array.isArray(parsedFiles) || parsedFiles.length === 0) {
                return new AnalysisResults({}, 0, 0);
            }

            // Convert to legacy format for existing analyzer
            const fileDataList = parsedFiles.map(pf => ({
                'name': pf.name,
                'data': this._convertParsedFileToDict(pf)
            }));

            // Run analysis
            const rawResults = runAnalysis(fileDataList);

            // Convert to domain models
            const analysisResults = {};
            let totalMetrics = 0;

            for (const [category, metricsMap] of Object.entries(rawResults)) {
                const metricDataDict = {};

                for (const [metric, data] of Object.entries(metricsMap)) {
                    metricDataDict[metric] = new MetricData(
                        data.values,
                        data.flags,
                        data.delta,
                        data.percentChange,
                        data.stdDev
                    );
                    totalMetrics++;
                }

                analysisResults[category] = new AnalysisResult(category, metricDataDict);
            }

            return new AnalysisResults(analysisResults, parsedFiles.length, totalMetrics);
        } catch (error) {
            throw new AnalysisError(`Analysis failed: ${error.message}`);
        }
    }

    /**
     * Convert ParsedFile to dictionary format for legacy analyzer
     * @private
     * @param {ParsedFile} parsedFile - ParsedFile domain model
     * @returns {Object} Dictionary format
     */
    static _convertParsedFileToDict(parsedFile) {
        const result = {};

        for (const [category, metrics] of Object.entries(parsedFile.data)) {
            result[category] = {};

            for (const [metric, metricValue] of Object.entries(metrics)) {
                result[category][metric] = {
                    'value': metricValue.value,
                    'isFlagged': metricValue.isFlagged
                };
            }
        }

        return result;
    }

    /**
     * Analyze files using dictionary format (legacy compatibility)
     * @param {Array} fileDataList - List of file data dictionaries
     * @returns {Object} Dictionary with analysis results
     */
    static analyzeFilesDict(fileDataList) {
        return runAnalysis(fileDataList);
    }
}

// Export service
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AnalysisService };
} else if (typeof window !== 'undefined') {
    window.VNGServices = window.VNGServices || {};
    window.VNGServices.AnalysisService = AnalysisService;
}
