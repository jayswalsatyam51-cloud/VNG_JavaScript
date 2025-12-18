# VNG Data Analyzer - JavaScript Version

A modern web-based application for analyzing and comparing VNG (Videonystagmography) test reports. Compare multiple VNG reports, track changes over time, visualize trends with interactive charts.

## ✨ Features

### 📊 Data Analysis
- **Multi-file Upload**: Upload and compare multiple VNG report files (.txt format)
- **Statistical Analysis**: Calculate delta, percent change, and standard deviation across reports
- **Flag Detection**: Identify metrics that were flagged as out-of-range in original reports
- **File Preview**: View file metadata and validation status

### 📈 Interactive Visualizations
- **Line Charts**: Individual metric trends with flagged value indicators
- **Bar Charts**: Category comparison with multiple file visualization
- **Heatmap**: Color-coded view of all metrics across all files
- **Interactive Charts**: Built with Chart.js for smooth interactions

### 📋 Enhanced Data Tables
- **Search & Filter**: Filter metrics by category
- **Detailed Analysis**: View all metrics with statistical calculations
- **Export Ready**: Data structured for easy export

## 🚀 Quick Start

### Option 1: Run Locally with HTTP Server

1. **Install dependencies** (optional - Chart.js is loaded via CDN):
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   # or
   npx http-server . -p 3000 -o
   ```

3. **Open your browser** to `http://localhost:3000`

### Option 2: Open Directly in Browser

Simply open `index.html` in your web browser. No server required!

## 📖 Usage

### Basic Workflow

1. **Upload Files**:
   - Click "Choose Files" and select one or more .txt VNG report files
   - View file validation status and metadata

2. **Analyze**:
   - Click "Analyze Files" to process and compare the reports
   - View real-time progress during analysis

3. **Explore Results**:
   - **Overview Tab**: See summary statistics and heatmap visualization
   - **Charts Tab**: Select from different chart types to visualize your data
   - **Detailed Analysis Tab**: Browse detailed tables with filtering
   - **AI Interpretation Tab**: Placeholder for future AI features

### Chart Types

- **Line Chart**: Best for tracking individual metric trends over time
- **Category Comparison**: Compare all metrics within a category across files
- **Radar Chart**: Coming soon - polar comparison view

## 📁 Project Structure

```
js/
├── index.html                 # Main HTML file
├── styles.css                 # Application styles
├── README.md                  # This file
├── package.json               # Node.js dependencies
└── src/
    ├── domain/                # Domain layer
    │   ├── models.js          # Domain models
    │   └── exceptions.js      # Custom exceptions
    ├── config/                # Configuration
    │   └── constants.js       # Application constants
    ├── utils/                 # Utility functions
    │   └── statistics.js      # Statistical calculations
    ├── modules/               # Core modules
    │   ├── parser.js          # VNG text parsing
    │   └── analyzer.js        # Statistical analysis
    ├── services/              # Service layer
    │   ├── parsingService.js  # Parsing service
    │   ├── analysisService.js # Analysis service
    │   ├── fileService.js     # File handling service
    │   └── visualizationService.js # Chart generation
    ├── repositories/          # Data access
    │   └── sessionRepository.js # Session storage
    └── app.js                 # Main application logic
```

## 🏗️ Architecture

The JavaScript version maintains the same layered architecture as the Python version:

### Layer Overview

1. **Domain Layer** (`domain/`): Core business models and entities
2. **Service Layer** (`services/`): Business logic orchestration
3. **Repository Layer** (`repositories/`): Session storage management
4. **UI Layer** (`app.js` + HTML): User interface and event handling
5. **Utilities** (`utils/`): Shared helper functions
6. **Modules** (`modules/`): Core parsing and analysis logic

## 🔧 Technical Details

### Dependencies
- **Chart.js**: Interactive charting library (loaded via CDN)
- **No server-side dependencies**: Runs entirely in the browser

### Browser Compatibility
- Modern browsers with ES6+ support
- File API support for file uploads
- Session Storage for data persistence

### File Processing
- Client-side file parsing (no data sent to servers)
- Supports UTF-8 encoded text files
- Real-time validation and error handling

## 🔄 Migration from Python

This JavaScript version maintains feature parity with the Python/Streamlit version:

### Converted Components
- ✅ VNG text parsing logic
- ✅ Statistical analysis functions
- ✅ Domain models and data structures
- ✅ File validation and handling
- ✅ Chart generation (Chart.js instead of Plotly)
- ✅ Session state management

### UI/UX Adaptations
- **Tabbed Interface**: Converted Streamlit tabs to HTML/CSS tabs
- **File Upload**: Streamlit file uploader → HTML5 file input
- **Charts**: Plotly charts → Chart.js charts
- **Tables**: Streamlit dataframes → HTML tables
- **Session State**: Streamlit session → Browser sessionStorage

### Future Enhancements
- **AI Integration**: Backend API needed for AI interpretation
- **Data Export**: CSV/Excel export functionality
- **Advanced Charts**: Radar charts, correlation matrices
- **Progressive Web App**: Offline functionality

## 🐛 Known Limitations

1. **AI Features**: Require backend API integration
2. **Advanced Export**: Limited to browser-based export
3. **Large Files**: Limited by browser memory constraints
4. **Cross-browser**: May need polyfills for older browsers

## 🤝 Contributing

The codebase is structured for easy extension:

### Adding New Chart Types
1. Add chart generation logic to `visualizationService.js`
2. Add UI controls to `app.js`
3. Update HTML structure as needed

### Adding New Analysis Features
1. Extend statistical functions in `utils/statistics.js`
2. Update analysis logic in `modules/analyzer.js`
3. Add UI controls and display logic

### Improving UI/UX
1. Update `styles.css` for styling changes
2. Modify `index.html` for structure changes
3. Update event handling in `app.js`

## 📄 License

MIT License - see Python version for full license details.

## 🙏 Acknowledgments

- **Original Python Version**: Built with Streamlit and Pandas
- **Chart.js**: Powerful charting library for the web
- **VNG Medical Community**: For establishing testing standards
