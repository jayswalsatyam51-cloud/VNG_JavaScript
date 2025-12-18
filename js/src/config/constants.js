/**
 * Application constants for VNG Data Analyzer
 */

// Chart Color Scheme
const CHART_COLORS = [
    '#3B82F6',  // Blue
    '#10B981',  // Green
    '#EF4444',  // Red
    '#F59E0B',  // Amber
    '#8B5CF6',  // Purple
    '#EC4899',  // Pink
    '#6366F1',  // Indigo
    '#14B8A6',  // Teal
];

// File Upload Settings
const ALLOWED_FILE_TYPES = ['.txt'];
const MAX_FILE_SIZE_MB = 10;

// Analysis Settings
const MIN_FILES_FOR_COMPARISON = 1;
const MIN_FILES_FOR_TRENDLINE = 3;

// AI Interpretation Settings
const MAX_METRICS_FOR_INTERPRETATION = 15;

// UI Configuration
const APP_CONFIG = {
    title: "VNG Data Analyzer",
    subtitle: "Compare multiple VNG reports, track changes over time, and get AI-powered clinical interpretations",
    uploadInstructions: "Upload one or more VNG report files (.txt format) to begin analysis.",
    uploadHelp: "Select .txt files containing VNG test data. Multiple files can be uploaded for comparison.",
    analyzeButtonText: "Analyze Files",
    appIcon: "🩺"
};

// Export constants
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CHART_COLORS,
        ALLOWED_FILE_TYPES,
        MAX_FILE_SIZE_MB,
        MIN_FILES_FOR_COMPARISON,
        MIN_FILES_FOR_TRENDLINE,
        MAX_METRICS_FOR_INTERPRETATION,
        APP_CONFIG
    };
} else if (typeof window !== 'undefined') {
    window.VNGConstants = {
        CHART_COLORS,
        ALLOWED_FILE_TYPES,
        MAX_FILE_SIZE_MB,
        MIN_FILES_FOR_COMPARISON,
        MIN_FILES_FOR_TRENDLINE,
        MAX_METRICS_FOR_INTERPRETATION,
        APP_CONFIG
    };
}
