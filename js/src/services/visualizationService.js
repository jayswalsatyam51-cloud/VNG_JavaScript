/**
 * Visualization service for creating charts - JavaScript version
 * Uses Chart.js for rendering charts
 */

const { CHART_COLORS } = typeof module !== 'undefined' && module.exports
    ? require('../config/constants')
    : window.VNGConstants;

/**
 * Service for creating visualizations using Chart.js
 */
class VisualizationService {
    /**
     * Create a line chart for metric trends
     * @param {string} metricName - Name of the metric
     * @param {number[]} values - Array of values
     * @param {string[]} fileNames - Array of file names
     * @param {boolean[]} flags - Array of flag indicators
     * @param {boolean} showConfidence - Whether to show confidence intervals
     * @returns {Object} Chart.js configuration object
     */
    static createLineChart(metricName, values, fileNames, flags = [], showConfidence = false) {
        const datasets = [{
            label: metricName,
            data: values,
            borderColor: CHART_COLORS[0],
            backgroundColor: CHART_COLORS[0] + '20',
            borderWidth: 2,
            fill: false,
            pointRadius: flags.map(flag => flag ? 8 : 4),
            pointBackgroundColor: flags.map(flag => flag ? '#EF4444' : CHART_COLORS[0]),
            pointBorderColor: flags.map(flag => flag ? '#EF4444' : CHART_COLORS[0]),
            pointBorderWidth: 2
        }];

        // Add trendline if enough points
        if (values.length >= 3) {
            const trendline = this._calculateTrendline(values);
            if (trendline.length > 0) {
                datasets.push({
                    label: 'Trend',
                    data: trendline,
                    borderColor: '#6B7280',
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                });
            }
        }

        return {
            type: 'line',
            data: {
                labels: fileNames,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: `${metricName} Trend`
                    },
                    legend: {
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: (context) => {
                                const index = context.dataIndex;
                                if (flags[index]) {
                                    return '⚠️ FLAGGED';
                                }
                                return '';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'File'
                        }
                    }
                }
            }
        };
    }

    /**
     * Create a bar chart for category comparison
     * @param {string} categoryName - Name of the category
     * @param {Object} categoryMetrics - Metrics data for the category
     * @param {string[]} fileNames - Array of file names
     * @returns {Object} Chart.js configuration object
     */
    static createBarChart(categoryName, categoryMetrics, fileNames) {
        const metrics = Object.keys(categoryMetrics);
        const datasets = [];

        fileNames.forEach((fileName, fileIndex) => {
            const data = metrics.map(metric => {
                const metricData = categoryMetrics[metric];
                return metricData.values[fileIndex] || 0;
            });

            datasets.push({
                label: fileName,
                data: data,
                backgroundColor: CHART_COLORS[fileIndex % CHART_COLORS.length],
                borderColor: CHART_COLORS[fileIndex % CHART_COLORS.length],
                borderWidth: 1
            });
        });

        return {
            type: 'bar',
            data: {
                labels: metrics,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: `${categoryName} Comparison`
                    },
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Metric'
                        }
                    }
                }
            }
        };
    }

    /**
     * Create a heatmap visualization (using a table representation)
     * @param {Object} analysisResults - Analysis results
     * @param {Array} fileDataList - List of file data
     * @returns {Object} Heatmap data structure for rendering
     */
    static createHeatmap(analysisResults, fileDataList) {
        const heatmapData = {
            categories: [],
            metrics: [],
            values: [],
            fileNames: fileDataList.map(f => f.name)
        };

        const categories = Object.keys(analysisResults).sort();

        categories.forEach(category => {
            const categoryMetrics = Object.keys(analysisResults[category]).sort();

            categoryMetrics.forEach(metric => {
                heatmapData.categories.push(category);
                heatmapData.metrics.push(`${category}: ${metric}`);
                heatmapData.values.push(analysisResults[category][metric].values);
            });
        });

        return heatmapData;
    }

    /**
     * Calculate simple trendline
     * @private
     * @param {number[]} values - Array of values
     * @returns {number[]} Trendline values
     */
    static _calculateTrendline(values) {
        const n = values.length;
        if (n < 2) return [];

        const xValues = Array.from({length: n}, (_, i) => i);
        const validPoints = [];

        for (let i = 0; i < n; i++) {
            if (values[i] !== null && values[i] !== undefined && !isNaN(values[i])) {
                validPoints.push([xValues[i], values[i]]);
            }
        }

        if (validPoints.length < 2) return [];

        const sumX = validPoints.reduce((sum, [x]) => sum + x, 0);
        const sumY = validPoints.reduce((sum, [, y]) => sum + y, 0);
        const sumXY = validPoints.reduce((sum, [x, y]) => sum + x * y, 0);
        const sumXX = validPoints.reduce((sum, [x]) => sum + x * x, 0);

        const vn = validPoints.length;
        const denominator = vn * sumXX - sumX * sumX;

        if (denominator === 0) return [];

        const slope = (vn * sumXY - sumX * sumY) / denominator;
        const intercept = (sumY - slope * sumX) / vn;

        return xValues.map(x => slope * x + intercept);
    }
}

// Export service
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VisualizationService };
} else if (typeof window !== 'undefined') {
    window.VNGServices = window.VNGServices || {};
    window.VNGServices.VisualizationService = VisualizationService;
}
