/**
 * Domain models for VNG Data Analyzer - JavaScript version
 * Core business entities and data structures
 */

/**
 * Represents a single metric value with its flag status
 */
class MetricValue {
    constructor(value, isFlagged = false) {
        this.value = value;
        this.isFlagged = isFlagged;
    }
}

/**
 * Represents metric data across multiple files
 */
class MetricData {
    constructor(values, flags, delta = null, percentChange = null, stdDev = null) {
        this.values = values;
        this.flags = flags;
        this.delta = delta;
        this.percentChange = percentChange;
        this.stdDev = stdDev;
    }
}

/**
 * Represents a parsed VNG file
 */
class ParsedFile {
    constructor(name, data, sizeBytes = 0) {
        this.name = name;
        this.data = data; // {category: {metric: MetricValue}}
        this.uploadedAt = new Date();
        this.sizeBytes = sizeBytes;
    }
}

/**
 * Represents analysis results for a category
 */
class AnalysisResult {
    constructor(category, metrics) {
        this.category = category;
        this.metrics = metrics; // {metricName: MetricData}
    }
}

/**
 * Container for all analysis results
 */
class AnalysisResults {
    constructor(results, fileCount, totalMetrics) {
        this.results = results; // {category: AnalysisResult}
        this.fileCount = fileCount;
        this.totalMetrics = totalMetrics;
        this.createdAt = new Date();
    }
}

/**
 * Information about uploaded files
 */
class FileUploadInfo {
    constructor(name, sizeBytes) {
        this.name = name;
        this.sizeBytes = sizeBytes;
        this.uploadedAt = new Date();
    }
}

// Export classes for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        MetricValue,
        MetricData,
        ParsedFile,
        AnalysisResult,
        AnalysisResults,
        FileUploadInfo
    };
} else if (typeof window !== 'undefined') {
    window.VNGDomain = {
        MetricValue,
        MetricData,
        ParsedFile,
        AnalysisResult,
        AnalysisResults,
        FileUploadInfo
    };
}
