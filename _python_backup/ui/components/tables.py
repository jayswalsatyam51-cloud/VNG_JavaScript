"""
Enhanced table components with sorting, filtering, and export
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from utils.formatters import format_number, format_percentage


def render_enhanced_table(
    analysis_results: Dict[str, Any],
    file_data_list: List[Dict],
    category: str = None
) -> None:
    """
    Render enhanced data table with sorting, filtering, and export
    
    Args:
        analysis_results: Analysis results dictionary
        file_data_list: List of file data
        category: Optional category to filter by
    """
    # Search/filter input
    search_term = st.text_input(
        "🔍 Search metrics",
        key="metric_search",
        placeholder="Type to search metrics..."
    )
    
    # Get categories to display
    categories = [category] if category else sorted(analysis_results.keys())
    
    # Build table data
    all_rows = []
    for cat in categories:
        if cat not in analysis_results:
            continue
        
        category_metrics = analysis_results[cat]
        for metric in sorted(category_metrics.keys()):
            # Filter by search term
            if search_term and search_term.lower() not in metric.lower() and search_term.lower() not in cat.lower():
                continue
            
            data = category_metrics[metric]
            row = {
                'Category': cat,
                'Test Name': metric,
            }
            
            # Add file columns
            for i, value in enumerate(data['values']):
                flag_indicator = " ⚠️" if data['flags'][i] else ""
                row[f'File {i+1}'] = f"{value:.2f}{flag_indicator}"
            
            # Add statistics columns
            row['Abs. Change (Δ)'] = format_number(data['delta'], 2)
            row['Perc. Change (%)'] = format_percentage(data['percent_change'], 2) if data['percent_change'] is not None else "N/A"
            row['Std. Dev (σ)'] = format_number(data['std_dev'], 2)
            
            # Add flag for row highlighting
            row['_has_flag'] = any(data['flags'])
            row['_has_significant_change'] = data['percent_change'] is not None and abs(data['percent_change']) > 10
            
            all_rows.append(row)
    
    if not all_rows:
        st.info("No metrics found matching your search criteria.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_rows)
    
    # Remove internal columns for display
    display_df = df.drop(columns=['_has_flag', '_has_significant_change'])
    
    # Apply color coding using st.dataframe with column configuration
    column_config = {}
    for col in display_df.columns:
        if col == 'Category':
            column_config[col] = st.column_config.TextColumn(col, width="medium")
        elif col == 'Test Name':
            column_config[col] = st.column_config.TextColumn(col, width="large")
        elif 'File' in col:
            column_config[col] = st.column_config.TextColumn(col, width="small")
        else:
            column_config[col] = st.column_config.TextColumn(col, width="small")
    
    # Display table with styling
    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config=column_config
    )
    
    # Export buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name="vng_analysis_results.csv",
            mime="text/csv"
        )
    with col2:
        # Excel export (requires openpyxl)
        try:
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Analysis Results')
            excel_data = output.getvalue()
            st.download_button(
                label="📊 Export Excel",
                data=excel_data,
                file_name="vng_analysis_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("💡 Install openpyxl for Excel export: pip install openpyxl")

