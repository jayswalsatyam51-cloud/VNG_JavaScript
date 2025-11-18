"""
VNG Data Analyzer - Streamlit Application
Main entry point for the VNG data analysis tool
"""

import streamlit as st
from typing import Dict, List

# New architecture imports
from repositories.session_repository import SessionRepository
from services.file_service import FileService
from services.parsing_service import ParsingService
from services.analysis_service import AnalysisService
from config.ui_config import (
    APP_TITLE, APP_SUBTITLE, UPLOAD_INSTRUCTIONS, UPLOAD_HELP,
    ANALYZE_BUTTON_TEXT, APP_ICON, PAGE_LAYOUT, INITIAL_SIDEBAR_STATE
)
from domain.exceptions import VNGError, ValidationError, ParsingError, FileError

# Legacy imports for backward compatibility
from modules.visualizer import render_category_chart

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# Initialize session state
SessionRepository.initialize()

# Apply custom styling
from ui.layouts.main_layout import apply_custom_styling
apply_custom_styling()


def main():
    """Main application function"""
    
    # Header
    st.title(APP_TITLE)
    st.markdown(f"*{APP_SUBTITLE}*")
    st.divider()
    
    # File Upload Section (always visible)
    from ui.components.file_upload import render_file_upload_section
    uploaded_files = render_file_upload_section()
    
    # Analyze Button
    analyze_button = st.button(
        ANALYZE_BUTTON_TEXT,
        type="primary",
        disabled=not uploaded_files or len(uploaded_files) == 0
    )
    
    # Handle Analysis
    if analyze_button and uploaded_files:
        with st.spinner("Analyzing data... this may take a moment."):
            try:
                # Parse all files using service layer
                parsed_files = []
                for file in uploaded_files:
                    try:
                        # Validate file
                        FileService.validate_file(file.name, len(file.getvalue()))
                        
                        # Read and parse file
                        file_content = FileService.read_file_content(file)
                        parsed_file = ParsingService.parse_file(
                            file.name,
                            file_content,
                            len(file.getvalue())
                        )
                        parsed_files.append(parsed_file)
                    except (ValidationError, ParsingError, FileError) as e:
                        st.error(f"Error processing file {file.name}: {str(e)}")
                        return
                    except Exception as e:
                        st.error(f"Unexpected error processing file {file.name}: {str(e)}")
                        return
                
                if not parsed_files:
                    st.error("No valid files were processed.")
                    return
                
                # Run analysis using service layer
                analysis_results = AnalysisService.analyze_files(parsed_files)
                
                # Convert to legacy format for UI compatibility
                file_data_list = [
                    {
                        'name': pf.name,
                        'data': {
                            category: {
                                metric: {
                                    'value': mv.value,
                                    'is_flagged': mv.is_flagged
                                }
                                for metric, mv in metrics.items()
                            }
                            for category, metrics in pf.data.items()
                        }
                    }
                    for pf in parsed_files
                ]
                
                # Convert analysis results to legacy format
                analysis_results_dict = {
                    category: {
                        metric: {
                            'values': data.values,
                            'flags': data.flags,
                            'delta': data.delta,
                            'percent_change': data.percent_change,
                            'std_dev': data.std_dev
                        }
                        for metric, data in result.metrics.items()
                    }
                    for category, result in analysis_results.results.items()
                }
                
                # Store in session state
                SessionRepository.set_file_data_list(file_data_list)
                SessionRepository.set_analysis_results(analysis_results_dict)
                SessionRepository.clear_selection()
                SessionRepository.clear_interpretation()
                
                st.success(
                    f"Analysis complete! Found {analysis_results.total_metrics} "
                    f"common tests across {analysis_results.file_count} files."
                )
            except VNGError as e:
                st.error(f"Analysis error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error during analysis: {str(e)}")
    
    # Results Section with Tabs
    analysis_results = SessionRepository.get_analysis_results()
    file_data_list = SessionRepository.get_file_data_list()
    
    if analysis_results and file_data_list:
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Charts", "📋 Detailed Analysis", "🤖 AI Interpretation"])
        
        with tab1:
            display_overview_tab(analysis_results, file_data_list)
        
        with tab2:
            display_charts_tab(analysis_results, file_data_list)
        
        with tab3:
            display_detailed_analysis_tab(analysis_results, file_data_list)
        
        with tab4:
            from ui.components.interpretation import render_interpretation_section
            render_interpretation_section()


def display_overview_tab(analysis_results: Dict, file_data_list: List[Dict]):
    """Display overview tab with dashboard and summary"""
    from ui.components.dashboard import render_summary_cards, render_quick_stats
    
    st.header("📊 Dashboard Overview")
    
    # Report generation section
    with st.expander("📄 Generate Comprehensive Report", expanded=False):
        st.write("Export a comprehensive report with all analysis data, statistics, and visualizations.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Generate and download CSV report
            import pandas as pd
            from io import StringIO
            
            # Prepare comprehensive data
            report_data = []
            for category, metrics in analysis_results.items():
                for metric, data in metrics.items():
                    row = {
                        'Category': category,
                        'Metric': metric,
                    }
                    # Add file values
                    for idx, file_data in enumerate(file_data_list):
                        row[f'File {idx+1} ({file_data["name"]})'] = data['values'][idx] if idx < len(data['values']) else None
                        row[f'File {idx+1} Flagged'] = data['flags'][idx] if idx < len(data['flags']) else False
                    
                    # Add statistics
                    row['Delta'] = data.get('delta', 'N/A')
                    row['Percent Change'] = f"{data.get('percent_change', 'N/A'):.2f}%" if data.get('percent_change') is not None else 'N/A'
                    row['Std Deviation'] = data.get('std_dev', 'N/A')
                    
                    report_data.append(row)
            
            df_report = pd.DataFrame(report_data)
            csv_report = df_report.to_csv(index=False)
            
            st.download_button(
                label="📊 Download CSV Report",
                data=csv_report,
                file_name=f"vng_comprehensive_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download complete analysis data as CSV"
            )
        
        with col2:
            # Generate summary report as text
            from datetime import datetime
            summary_lines = [
                "VNG Analysis Comprehensive Report",
                "=" * 50,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Files Analyzed: {len(file_data_list)}",
                "",
                "Files:",
            ]
            for idx, file_data in enumerate(file_data_list):
                summary_lines.append(f"  {idx+1}. {file_data['name']}")
            
            summary_lines.extend([
                "",
                "Summary Statistics:",
                "-" * 30,
            ])
            
            # Calculate summary stats
            total_metrics = sum(len(metrics) for metrics in analysis_results.values())
            flagged_count = sum(1 for category_metrics in analysis_results.values() 
                              for metric_data in category_metrics.values() 
                              if any(metric_data.get('flags', [])))
            significant_changes = sum(1 for category_metrics in analysis_results.values() 
                                     for metric_data in category_metrics.values() 
                                     if metric_data.get('percent_change') is not None 
                                     and abs(metric_data['percent_change']) > 10)
            
            summary_lines.extend([
                f"Total Metrics: {total_metrics}",
                f"Flagged Metrics: {flagged_count}",
                f"Significant Changes (>10%): {significant_changes}",
                "",
                "=" * 50,
                "",
                "Detailed Results:",
                "-" * 30,
            ])
            
            for category, metrics in sorted(analysis_results.items()):
                summary_lines.append(f"\nCategory: {category}")
                for metric, data in sorted(metrics.items()):
                    summary_lines.append(f"  - {metric}:")
                    for idx, file_data in enumerate(file_data_list):
                        value = data['values'][idx] if idx < len(data['values']) else 'N/A'
                        flagged = " (FLAGGED)" if idx < len(data['flags']) and data['flags'][idx] else ""
                        summary_lines.append(f"    File {idx+1}: {value}{flagged}")
                    if data.get('percent_change') is not None:
                        summary_lines.append(f"    Percent Change: {data['percent_change']:.2f}%")
                    if data.get('std_dev') is not None:
                        summary_lines.append(f"    Std Deviation: {data['std_dev']:.2f}")
            
            summary_text = "\n".join(summary_lines)
            
            st.download_button(
                label="📄 Download Text Report",
                data=summary_text,
                file_name=f"vng_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="Download complete analysis as text report"
            )
        
        with col3:
            st.info("💡 **Report Generation**:\n\n"
                   "• **CSV Report**: Complete data with all metrics, values, and statistics\n"
                   "• **Text Report**: Human-readable summary with all findings\n\n"
                   "For AI interpretations, see the 'AI Interpretation' tab.")
    
    st.divider()
    
    # Summary cards
    render_summary_cards(analysis_results, file_data_list)
    
    st.divider()
    
    # Quick statistics
    render_quick_stats(analysis_results)
    
    st.divider()
    
    # Heatmap visualization
    st.subheader("🔥 Heatmap View")
    st.caption("Color-coded view of all metrics across all files")
    
    from ui.components.charts import render_heatmap
    try:
        heatmap_fig = render_heatmap(analysis_results, file_data_list)
        st.plotly_chart(heatmap_fig, width='stretch')
    except Exception as e:
        st.error(f"Error rendering heatmap: {str(e)}")


def display_charts_tab(analysis_results: Dict, file_data_list: List[Dict]):
    """Display charts tab with enhanced visualizations"""
    st.header("📈 Charts & Visualizations")
    
    # Chart type selector
    chart_type = st.radio(
        "Select Chart Type",
        ["Line Chart", "Category Comparison", "Radar Chart", "Box Plot", "Correlation Matrix"],
        horizontal=True,
        key="chart_type_selector"
    )
    
    if chart_type == "Line Chart":
        display_line_chart_selection(analysis_results, file_data_list)
    elif chart_type == "Category Comparison":
        display_category_chart_selection(analysis_results, file_data_list)
    elif chart_type == "Radar Chart":
        display_radar_chart_selection(analysis_results, file_data_list)
    elif chart_type == "Box Plot":
        display_box_plot_selection(analysis_results, file_data_list)
    elif chart_type == "Correlation Matrix":
        display_correlation_matrix_selection(analysis_results)


def display_detailed_analysis_tab(analysis_results: Dict, file_data_list: List[Dict]):
    """Display detailed analysis tab with enhanced tables"""
    st.header("📋 Detailed Analysis")
    
    from ui.components.tables import render_enhanced_table
    
    # Category filter
    category_options = ["All Categories"] + sorted(analysis_results.keys())
    selected_category = st.selectbox(
        "Filter by Category",
        category_options,
        key="category_filter"
    )
    
    category = None if selected_category == "All Categories" else selected_category
    
    # Render enhanced table
    render_enhanced_table(analysis_results, file_data_list, category)


def display_line_chart_selection(analysis_results: Dict, file_data_list: List[Dict]):
    """Display line chart selection interface"""
    # Category selection
    category = st.selectbox(
        "Select Category",
        sorted(analysis_results.keys()),
        key="line_chart_category"
    )
    
    if category:
        # Metric selection
        metrics = sorted(analysis_results[category].keys())
        metric = st.selectbox(
            "Select Metric",
            metrics,
            key="line_chart_metric"
        )
        
        if metric:
            from ui.components.charts import render_enhanced_line_chart
            
            metric_data = analysis_results[category][metric]
            file_names = [f['name'] for f in file_data_list]
            
            # Chart options
            show_confidence = st.checkbox("Show Confidence Intervals", key=f"conf_{category}_{metric}", value=False)
            
            fig = render_enhanced_line_chart(
                metric,
                metric_data['values'],
                file_names,
                flags=metric_data['flags'],
                show_confidence=show_confidence
            )
            st.plotly_chart(fig, width='stretch')
            
            # Export button
            export_chart_button(fig, f"line_{category}_{metric}")


def display_category_chart_selection(analysis_results: Dict, file_data_list: List[Dict]):
    """Display category chart selection interface"""
    category = st.selectbox(
        "Select Category",
        sorted(analysis_results.keys()),
        key="category_chart_category"
    )
    
    if category:
        category_metrics = analysis_results[category]
        file_names = [f['name'] for f in file_data_list]
        
        # Chart options
        col1, col2, col3 = st.columns(3)
        with col1:
            orientation = st.radio("Orientation", ["Vertical", "Horizontal"], key=f"bar_orient_{category}", horizontal=True)
        with col2:
            stacked = st.checkbox("Stacked Bars", key=f"stacked_{category}", value=False)
        with col3:
            show_gradients = st.checkbox("Color Gradients", key=f"gradient_{category}", value=False)
        
        # Use enhanced bar chart if options are selected
        if orientation == "Horizontal" or stacked or show_gradients:
            from ui.components.charts import render_enhanced_bar_chart
            fig = render_enhanced_bar_chart(
                category,
                category_metrics,
                file_names,
                orientation=orientation.lower(),
                stacked=stacked,
                show_gradients=show_gradients
            )
            show_disclaimer = len(file_data_list) > 1
        else:
            fig, show_disclaimer = render_category_chart(
                category,
                category_metrics,
                file_names,
                file_data_list
            )
        
        st.plotly_chart(fig, width='stretch')
        
        if show_disclaimer:
            st.info(
                "Values are shown as % change from File 1 to normalize different scales "
                "(e.g., msec vs. %). Raw values are in the table and the single-metric line chart."
            )
        
        # Export button
        export_chart_button(fig, f"category_{category}")


def display_radar_chart_selection(analysis_results: Dict, file_data_list: List[Dict]):
    """Display radar chart selection interface"""
    category = st.selectbox(
        "Select Category",
        sorted(analysis_results.keys()),
        key="radar_chart_category"
    )
    
    if category:
        from ui.components.charts import render_radar_chart
        
        try:
            fig = render_radar_chart(analysis_results, file_data_list, category)
            st.plotly_chart(fig, width='stretch')
            
            # Export button
            col1, col2 = st.columns([1, 4])
            with col1:
                export_chart_button(fig, f"radar_{category}")
        except Exception as e:
            st.error(f"Error rendering radar chart: {str(e)}")


def display_box_plot_selection(analysis_results: Dict, file_data_list: List[Dict]):
    """Display box plot selection interface"""
    if len(file_data_list) < 3:
        st.warning("Box plots require at least 3 files for meaningful distribution analysis.")
        return
    
    category = st.selectbox(
        "Select Category",
        sorted(analysis_results.keys()),
        key="box_plot_category"
    )
    
    if category:
        metrics = sorted(analysis_results[category].keys())
        metric = st.selectbox(
            "Select Metric",
            metrics,
            key="box_plot_metric"
        )
        
        if metric:
            from ui.components.charts import render_box_plot
            
            try:
                fig = render_box_plot(analysis_results, file_data_list, category, metric)
                st.plotly_chart(fig, width='stretch')
                
                # Export button
                export_chart_button(fig, f"boxplot_{category}_{metric}")
            except Exception as e:
                st.error(f"Error rendering box plot: {str(e)}")


def display_correlation_matrix_selection(analysis_results: Dict):
    """Display correlation matrix selection interface"""
    st.info(
        "**Correlation Matrix**: Shows how metrics in a category relate to each other. "
        "Values range from -1 to +1: "
        "+1 = strong positive correlation (metrics increase together), "
        "-1 = strong negative correlation (one increases as other decreases), "
        "0 = no correlation. "
        "This helps identify which metrics tend to change together across files."
    )
    
    category = st.selectbox(
        "Select Category",
        sorted(analysis_results.keys()),
        key="correlation_category"
    )
    
    if category:
        if len(analysis_results[category]) < 2:
            st.warning("Correlation matrix requires at least 2 metrics in the category.")
            return
        
        from ui.components.charts import render_correlation_matrix
        
        try:
            fig = render_correlation_matrix(analysis_results, category)
            st.plotly_chart(fig, width='stretch')
            
            # Export button
            export_chart_button(fig, f"correlation_{category}")
        except Exception as e:
            st.error(f"Error rendering correlation matrix: {str(e)}")


def export_chart_button(fig, chart_name: str):
    """Add export button for charts"""
    import plotly.io as pio
    
    # HTML export (interactive)
    html_str = pio.to_html(fig, include_plotlyjs='cdn')
    st.download_button(
        label="🌐 Export HTML",
        data=html_str,
        file_name=f"{chart_name}.html",
        mime="text/html"
    )






if __name__ == "__main__":
    main()

