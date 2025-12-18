/**
 * Main application for VNG Data Analyzer - JavaScript version
 */

// Global state
let uploadedFiles = [];
let parsedFiles = [];
let analysisResults = null;
let currentChart = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize repositories
    if (window.VNGRepositories && window.VNGRepositories.SessionRepository) {
        window.VNGRepositories.SessionRepository.initialize();
    }

    // Setup event listeners
    setupEventListeners();

    // Load any existing session data
    loadSessionData();

    // Update UI state
    updateUI();
}

function setupEventListeners() {
    // File input
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', handleFileSelection);

    // Analyze button
    const analyzeBtn = document.getElementById('analyze-btn');
    analyzeBtn.addEventListener('click', handleAnalysis);

    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });

    // Chart controls
    const chartTypeSelect = document.getElementById('chart-type-select');
    chartTypeSelect.addEventListener('change', handleChartTypeChange);
}

function handleFileSelection(event) {
    const files = Array.from(event.target.files);
    uploadedFiles = files;

    // Validate and display files
    displayFileList(files);

    // Update analyze button
    updateAnalyzeButton();
}

function displayFileList(files) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';

    files.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        try {
            // Validate file
            window.VNGServices.FileService.validateFile(file.name, file.size);
            fileItem.classList.add('valid');

            fileItem.innerHTML = `
                <span>${file.name} (${(file.size / 1024).toFixed(1)} KB)</span>
                <span class="file-status">✓ Valid</span>
            `;
        } catch (error) {
            fileItem.classList.add('invalid');
            fileItem.innerHTML = `
                <span>${file.name} (${(file.size / 1024).toFixed(1)} KB)</span>
                <span class="file-status error">${error.message}</span>
            `;
        }

        fileList.appendChild(fileItem);
    });
}

function updateAnalyzeButton() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const validFiles = uploadedFiles.filter(file => {
        try {
            window.VNGServices.FileService.validateFile(file.name, file.size);
            return true;
        } catch {
            return false;
        }
    });

    analyzeBtn.disabled = validFiles.length === 0;
}

async function handleAnalysis() {
    if (uploadedFiles.length === 0) return;

    // Show loading overlay
    showLoading(true);

    try {
        // Parse all files
        parsedFiles = [];
        for (const file of uploadedFiles) {
            try {
                // Validate file
                window.VNGServices.FileService.validateFile(file.name, file.size);

                // Read and parse file
                const fileContent = await window.VNGServices.FileService.readFileContent(file);
                const parsedFile = window.VNGServices.ParsingService.parseFile(
                    file.name,
                    fileContent,
                    file.size
                );
                parsedFiles.push(parsedFile);
            } catch (error) {
                console.error(`Error processing file ${file.name}:`, error);
                showError(`Error processing file ${file.name}: ${error.message}`);
                return;
            }
        }

        if (parsedFiles.length === 0) {
            showError("No valid files were processed.");
            return;
        }

        // Run analysis
        analysisResults = window.VNGServices.AnalysisService.analyzeFiles(parsedFiles);

        // Save to session
        saveSessionData();

        // Show results
        showResults();

        // Display overview
        displayOverview();

        showSuccess(`Analysis complete! Found ${analysisResults.totalMetrics} common tests across ${analysisResults.fileCount} files.`);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Analysis error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function showResults() {
    document.getElementById('results-section').style.display = 'block';
    document.getElementById('upload-section').style.display = 'none';
}

function displayOverview() {
    // Summary cards
    displaySummaryCards();

    // Heatmap
    displayHeatmap();
}

function displaySummaryCards() {
    const summaryCards = document.getElementById('summary-cards');
    summaryCards.innerHTML = '';

    if (!analysisResults) return;

    const cards = [
        {
            title: analysisResults.fileCount.toString(),
            label: 'Files Analyzed'
        },
        {
            title: analysisResults.totalMetrics.toString(),
            label: 'Total Metrics'
        },
        {
            title: countFlaggedMetrics().toString(),
            label: 'Flagged Metrics'
        },
        {
            title: countSignificantChanges().toString(),
            label: 'Significant Changes'
        }
    ];

    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'summary-card';
        cardElement.innerHTML = `
            <h3>${card.title}</h3>
            <p>${card.label}</p>
        `;
        summaryCards.appendChild(cardElement);
    });
}

function countFlaggedMetrics() {
    let count = 0;
    for (const category of Object.values(analysisResults.results)) {
        for (const metricData of Object.values(category.metrics)) {
            if (metricData.flags.some(flag => flag)) {
                count++;
            }
        }
    }
    return count;
}

function countSignificantChanges() {
    let count = 0;
    for (const category of Object.values(analysisResults.results)) {
        for (const metricData of Object.values(category.metrics)) {
            if (metricData.percentChange !== null &&
                Math.abs(metricData.percentChange) > 10) {
                count++;
            }
        }
    }
    return count;
}

function displayHeatmap() {
    const container = document.getElementById('heatmap-container');

    if (!analysisResults || !parsedFiles.length) {
        container.innerHTML = '<p>No data to display</p>';
        return;
    }

    const heatmapData = window.VNGServices.VisualizationService.createHeatmap(
        convertAnalysisResultsToDict(analysisResults),
        convertParsedFilesToDict(parsedFiles)
    );

    // Create a simple table representation of heatmap
    let html = '<h3>📊 Heatmap View</h3>';
    html += '<p>Color-coded view of all metrics across all files</p>';
    html += '<div style="overflow-x: auto;">';
    html += '<table>';
    html += '<thead><tr><th>Metric</th>';

    heatmapData.fileNames.forEach(fileName => {
        html += `<th>${fileName}</th>`;
    });
    html += '</tr></thead><tbody>';

    heatmapData.metrics.forEach((metric, index) => {
        html += `<tr><td>${metric}</td>`;
        heatmapData.values[index].forEach(value => {
            const intensity = Math.min(Math.abs(value) / 100, 1); // Normalize to 0-1
            const color = value >= 0 ? `rgba(16, 185, 129, ${intensity})` : `rgba(239, 68, 68, ${intensity})`;
            html += `<td style="background-color: ${color}; color: white; text-align: center;">${value !== null ? value.toFixed(2) : 'N/A'}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function convertAnalysisResultsToDict(analysisResults) {
    const result = {};
    for (const [categoryName, category] of Object.entries(analysisResults.results)) {
        result[categoryName] = {};
        for (const [metricName, metricData] of Object.entries(category.metrics)) {
            result[categoryName][metricName] = {
                values: metricData.values,
                flags: metricData.flags,
                delta: metricData.delta,
                percentChange: metricData.percentChange,
                stdDev: metricData.stdDev
            };
        }
    }
    return result;
}

function convertParsedFilesToDict(parsedFiles) {
    return parsedFiles.map(pf => ({
        name: pf.name,
        data: convertParsedFileDataToDict(pf.data)
    }));
}

function convertParsedFileDataToDict(data) {
    const result = {};
    for (const [category, metrics] of Object.entries(data)) {
        result[category] = {};
        for (const [metric, metricValue] of Object.entries(metrics)) {
            result[category][metric] = {
                value: metricValue.value,
                isFlagged: metricValue.isFlagged
            };
        }
    }
    return result;
}

function switchTab(tabName) {
    // Update tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tabName);
    });

    // Update tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    // Load tab content
    switch (tabName) {
        case 'overview':
            displayOverview();
            break;
        case 'charts':
            displayChartsTab();
            break;
        case 'detailed':
            displayDetailedTab();
            break;
        case 'ai':
            displayAITab();
            break;
    }
}

function displayChartsTab() {
    const chartType = document.getElementById('chart-type-select').value;
    handleChartTypeChange({ target: { value: chartType } });
}

function handleChartTypeChange(event) {
    const chartType = event.target.value;
    const controlsContainer = document.getElementById('chart-controls');
    const chartContainer = document.getElementById('chart-container');

    controlsContainer.innerHTML = '';

    if (!analysisResults) {
        chartContainer.innerHTML = '<p>No analysis results available</p>';
        return;
    }

    const categories = Object.keys(analysisResults.results);

    switch (chartType) {
        case 'line':
            displayLineChartControls(controlsContainer, chartContainer, categories);
            break;
        case 'bar':
            displayBarChartControls(controlsContainer, chartContainer, categories);
            break;
        case 'radar':
            displayRadarChartControls(controlsContainer, chartContainer, categories);
            break;
    }
}

function displayLineChartControls(controlsContainer, chartContainer, categories) {
    if (categories.length === 0) {
        chartContainer.innerHTML = '<p>No categories available</p>';
        return;
    }

    const categorySelect = document.createElement('select');
    categorySelect.id = 'line-category-select';

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Category';
    categorySelect.appendChild(defaultOption);

    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    });

    const metricSelect = document.createElement('select');
    metricSelect.id = 'line-metric-select';
    metricSelect.disabled = true;

    categorySelect.addEventListener('change', () => {
        updateMetricSelect(metricSelect, categorySelect.value);
        renderLineChart(chartContainer, categorySelect.value, metricSelect.value);
    });

    metricSelect.addEventListener('change', () => {
        renderLineChart(chartContainer, categorySelect.value, metricSelect.value);
    });

    controlsContainer.appendChild(categorySelect);
    controlsContainer.appendChild(metricSelect);
}

function updateMetricSelect(metricSelect, category) {
    metricSelect.innerHTML = '';

    if (!category || !analysisResults.results[category]) {
        metricSelect.disabled = true;
        return;
    }

    metricSelect.disabled = false;
    const metrics = Object.keys(analysisResults.results[category]);

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Metric';
    metricSelect.appendChild(defaultOption);

    metrics.forEach(metric => {
        const option = document.createElement('option');
        option.value = metric;
        option.textContent = metric;
        metricSelect.appendChild(option);
    });
}

function renderLineChart(container, category, metric) {
    if (!category || !metric || !analysisResults.results[category]?.[metric]) {
        container.innerHTML = '<p>Please select a category and metric</p>';
        return;
    }

    const metricData = analysisResults.results[category][metric];
    const fileNames = parsedFiles.map(pf => pf.name);

    const chartConfig = window.VNGServices.VisualizationService.createLineChart(
        metric,
        metricData.values,
        fileNames,
        metricData.flags,
        false
    );

    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }

    const canvas = document.createElement('canvas');
    container.innerHTML = '';
    container.appendChild(canvas);

    currentChart = new Chart(canvas, chartConfig);
}

function displayBarChartControls(controlsContainer, chartContainer, categories) {
    if (categories.length === 0) {
        chartContainer.innerHTML = '<p>No categories available</p>';
        return;
    }

    const categorySelect = document.createElement('select');
    categorySelect.id = 'bar-category-select';

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Category';
    categorySelect.appendChild(defaultOption);

    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    });

    categorySelect.addEventListener('change', () => {
        renderBarChart(chartContainer, categorySelect.value);
    });

    controlsContainer.appendChild(categorySelect);
}

function renderBarChart(container, category) {
    if (!category || !analysisResults.results[category]) {
        container.innerHTML = '<p>Please select a category</p>';
        return;
    }

    const categoryData = analysisResults.results[category];
    const fileNames = parsedFiles.map(pf => pf.name);

    const chartConfig = window.VNGServices.VisualizationService.createBarChart(
        category,
        convertCategoryMetricsToDict(categoryData),
        fileNames
    );

    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }

    const canvas = document.createElement('canvas');
    container.innerHTML = '';
    container.appendChild(canvas);

    currentChart = new Chart(canvas, chartConfig);
}

function convertCategoryMetricsToDict(categoryData) {
    const result = {};
    for (const [metricName, metricData] of Object.entries(categoryData.metrics)) {
        result[metricName] = {
            values: metricData.values,
            flags: metricData.flags
        };
    }
    return result;
}

function displayRadarChartControls(controlsContainer, chartContainer, categories) {
    controlsContainer.innerHTML = '<p>Radar chart implementation coming soon...</p>';
    chartContainer.innerHTML = '<p>Radar chart visualization would be displayed here</p>';
}

function displayDetailedTab() {
    const categoryFilter = document.getElementById('category-filter');
    const dataTable = document.getElementById('data-table');

    // Populate category filter
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    if (analysisResults) {
        Object.keys(analysisResults.results).forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }

    categoryFilter.addEventListener('change', () => {
        renderDetailedTable(dataTable, categoryFilter.value);
    });

    renderDetailedTable(dataTable, '');
}

function renderDetailedTable(container, selectedCategory) {
    if (!analysisResults) {
        container.innerHTML = '<p>No analysis results available</p>';
        return;
    }

    let html = '<table>';
    html += '<thead><tr><th>Category</th><th>Metric</th>';

    parsedFiles.forEach(pf => {
        html += `<th>${pf.name}</th><th>Flag</th>`;
    });

    html += '<th>Delta</th><th>% Change</th><th>Std Dev</th></tr></thead><tbody>';

    for (const [categoryName, category] of Object.entries(analysisResults.results)) {
        if (selectedCategory && selectedCategory !== categoryName) continue;

        for (const [metricName, metricData] of Object.entries(category.metrics)) {
            html += `<tr><td>${categoryName}</td><td>${metricName}</td>`;

            metricData.values.forEach((value, index) => {
                const flagClass = metricData.flags[index] ? 'flag-indicator' : '';
                html += `<td>${value !== null ? value.toFixed(2) : 'N/A'}</td>`;
                html += `<td class="${flagClass}">${metricData.flags[index] ? '⚠️' : ''}</td>`;
            });

            html += `<td>${metricData.delta !== null ? metricData.delta.toFixed(2) : 'N/A'}</td>`;
            html += `<td>${metricData.percentChange !== null ? metricData.percentChange.toFixed(2) + '%' : 'N/A'}</td>`;
            html += `<td>${metricData.stdDev !== null ? metricData.stdDev.toFixed(2) : 'N/A'}</td>`;

            html += '</tr>';
        }
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function displayAITab() {
    const aiSection = document.getElementById('ai-interpretation');
    aiSection.innerHTML = `
        <h3>🤖 AI Interpretation</h3>
        <p>AI-powered clinical interpretation requires backend API integration.</p>
        <p>This feature would analyze your VNG results and provide clinical insights using advanced AI models.</p>
        <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin-top: 20px;">
            <h4>Coming Soon:</h4>
            <ul>
                <li>Clinical analysis of VNG patterns</li>
                <li>Web search integration for normative data</li>
                <li>Test-retest reliability assessment</li>
                <li>Automated report generation</li>
            </ul>
        </div>
    `;
}

function saveSessionData() {
    if (window.VNGRepositories && window.VNGRepositories.SessionRepository) {
        const fileDataList = convertParsedFilesToDict(parsedFiles);
        const analysisResultsDict = convertAnalysisResultsToDict(analysisResults);

        window.VNGRepositories.SessionRepository.setFileDataList(fileDataList);
        window.VNGRepositories.SessionRepository.setAnalysisResults(analysisResultsDict);
    }
}

function loadSessionData() {
    if (window.VNGRepositories && window.VNGRepositories.SessionRepository) {
        const fileDataList = window.VNGRepositories.SessionRepository.getFileDataList();
        const analysisResultsDict = window.VNGRepositories.SessionRepository.getAnalysisResults();

        if (fileDataList && analysisResultsDict) {
            // Restore from session
            parsedFiles = fileDataList.map(item => {
                const parsedFile = window.VNGServices.ParsingService.parseFile(
                    item.name,
                    '', // We don't have the content, but we can reconstruct from data
                    0
                );
                parsedFile.data = item.data;
                return parsedFile;
            });

            analysisResults = analysisResultsDict;
            showResults();
            displayOverview();
        }
    }
}

function updateUI() {
    // Update any dynamic UI elements
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(errorDiv, container.firstChild);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(successDiv, container.firstChild);

    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}
