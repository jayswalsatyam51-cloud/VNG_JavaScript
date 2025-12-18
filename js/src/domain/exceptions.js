/**
 * Custom exception classes for VNG Data Analyzer
 */

/**
 * Base VNG error class
 */
class VNGError extends Error {
    constructor(message) {
        super(message);
        this.name = 'VNGError';
    }
}

/**
 * Validation error for input validation
 */
class ValidationError extends VNGError {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

/**
 * Parsing error for file parsing issues
 */
class ParsingError extends VNGError {
    constructor(message) {
        super(message);
        this.name = 'ParsingError';
    }
}

/**
 * File handling error
 */
class FileError extends VNGError {
    constructor(message) {
        super(message);
        this.name = 'FileError';
    }
}

/**
 * Analysis error for data analysis issues
 */
class AnalysisError extends VNGError {
    constructor(message) {
        super(message);
        this.name = 'AnalysisError';
    }
}

// Export exceptions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        VNGError,
        ValidationError,
        ParsingError,
        FileError,
        AnalysisError
    };
} else if (typeof window !== 'undefined') {
    window.VNGExceptions = {
        VNGError,
        ValidationError,
        ParsingError,
        FileError,
        AnalysisError
    };
}
