/**
 * File handling service - JavaScript version
 */

const { FileUploadInfo } = typeof module !== 'undefined' && module.exports
    ? require('../domain/models')
    : window.VNGDomain;

const { FileError, ValidationError } = typeof module !== 'undefined' && module.exports
    ? require('../domain/exceptions')
    : window.VNGExceptions;

const { ALLOWED_FILE_TYPES, MAX_FILE_SIZE_MB } = typeof module !== 'undefined' && module.exports
    ? require('../config/constants')
    : window.VNGConstants;

/**
 * Service for file operations
 */
class FileService {
    /**
     * Validate uploaded file
     * @param {string} fileName - Name of the file
     * @param {number} fileSize - Size of the file in bytes
     */
    static validateFile(fileName, fileSize) {
        // Check file extension
        const isAllowedType = ALLOWED_FILE_TYPES.some(ext =>
            fileName.toLowerCase().endsWith(ext)
        );

        if (!isAllowedType) {
            throw new ValidationError(
                `File type not allowed. Allowed types: ${ALLOWED_FILE_TYPES.join(', ')}`
            );
        }

        // Check file size
        const sizeMB = fileSize / (1024 * 1024);
        if (sizeMB > MAX_FILE_SIZE_MB) {
            throw new ValidationError(
                `File size (${sizeMB.toFixed(2)} MB) exceeds maximum allowed size (${MAX_FILE_SIZE_MB} MB)`
            );
        }
    }

    /**
     * Read content from uploaded file
     * @param {File} uploadedFile - File object from input
     * @returns {Promise<string>} File content as string
     */
    static async readFileContent(uploadedFile) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (event) => {
                try {
                    resolve(event.target.result);
                } catch (error) {
                    reject(new FileError(`Failed to read file ${uploadedFile.name}: ${error.message}`));
                }
            };

            reader.onerror = () => {
                reject(new FileError(`Failed to read file ${uploadedFile.name}`));
            };

            reader.readAsText(uploadedFile);
        });
    }

    /**
     * Get file information
     * @param {File} uploadedFile - File object from input
     * @returns {FileUploadInfo} FileUploadInfo domain model
     */
    static getFileInfo(uploadedFile) {
        return new FileUploadInfo(
            uploadedFile.name,
            uploadedFile.size
        );
    }
}

// Export service
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FileService };
} else if (typeof window !== 'undefined') {
    window.VNGServices = window.VNGServices || {};
    window.VNGServices.FileService = FileService;
}
