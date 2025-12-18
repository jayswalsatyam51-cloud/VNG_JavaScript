/**
 * Session repository for managing application state - JavaScript version
 * Manages data persistence in browser session
 */

class SessionRepository {
    static initialize() {
        // Initialize session storage if needed
        if (typeof Storage === 'undefined') {
            console.warn('Session storage not supported');
        }
    }

    static setFileDataList(fileDataList) {
        try {
            sessionStorage.setItem('vng_fileDataList', JSON.stringify(fileDataList));
        } catch (error) {
            console.error('Failed to save file data list:', error);
        }
    }

    static getFileDataList() {
        try {
            const data = sessionStorage.getItem('vng_fileDataList');
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to load file data list:', error);
            return null;
        }
    }

    static setAnalysisResults(analysisResults) {
        try {
            sessionStorage.setItem('vng_analysisResults', JSON.stringify(analysisResults));
        } catch (error) {
            console.error('Failed to save analysis results:', error);
        }
    }

    static getAnalysisResults() {
        try {
            const data = sessionStorage.getItem('vng_analysisResults');
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to load analysis results:', error);
            return null;
        }
    }

    static clearSelection() {
        try {
            sessionStorage.removeItem('vng_selectedCategory');
            sessionStorage.removeItem('vng_selectedMetric');
        } catch (error) {
            console.error('Failed to clear selection:', error);
        }
    }

    static clearInterpretation() {
        try {
            sessionStorage.removeItem('vng_interpretation');
        } catch (error) {
            console.error('Failed to clear interpretation:', error);
        }
    }

    static clearAll() {
        try {
            const keys = Object.keys(sessionStorage).filter(key => key.startsWith('vng_'));
            keys.forEach(key => sessionStorage.removeItem(key));
        } catch (error) {
            console.error('Failed to clear session data:', error);
        }
    }
}

// Export repository
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SessionRepository };
} else if (typeof window !== 'undefined') {
    window.VNGRepositories = { SessionRepository };
}
