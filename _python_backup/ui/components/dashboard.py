"""
Dashboard component with summary cards and overview statistics
"""

import streamlit as st
from typing import Dict, List, Any
from domain.models import AnalysisResults
from utils.formatters import format_number, format_percentage


def render_summary_cards(analysis_results: Dict[str, Any], file_data_list: List[Dict]) -> None:
    """
    Render summary cards with key statistics
    
    Args:
        analysis_results: Analysis results dictionary
        file_data_list: List of file data
    """
    # Calculate statistics
    total_files = len(file_data_list)
    total_metrics = sum(len(metrics) for metrics in analysis_results.values())
    
    # Count flagged metrics
    flagged_count = 0
    significant_changes = 0
    
    for category, metrics in analysis_results.items():
        for metric, data in metrics.items():
            # Count flagged
            if any(data['flags']):
                flagged_count += 1
            
            # Count significant changes (>10% change)
            if data['percent_change'] is not None:
                if abs(data['percent_change']) > 10:
                    significant_changes += 1
    
    # Create columns for cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📁 Files Analyzed",
            value=total_files,
            help="Total number of VNG report files analyzed"
        )
    
    with col2:
        st.metric(
            label="📊 Total Metrics",
            value=total_metrics,
            help="Number of common metrics found across all files"
        )
    
    with col3:
        st.metric(
            label="⚠️ Flagged Metrics",
            value=flagged_count,
            help="Metrics that were flagged as out-of-range in original reports"
        )
    
    with col4:
        st.metric(
            label="📈 Significant Changes",
            value=significant_changes,
            help="Metrics with >10% change between files"
        )


def render_quick_stats(analysis_results: Dict[str, Any]) -> None:
    """
    Render quick statistics about the analysis
    
    Args:
        analysis_results: Analysis results dictionary
    """
    if not analysis_results:
        return
    
    st.subheader("📈 Quick Statistics")
    
    # Calculate averages - only show percentage-based metrics for consistency
    all_percent_changes = []
    all_std_devs = []
    
    for category, metrics in analysis_results.items():
        for metric, data in metrics.items():
            if data['percent_change'] is not None:
                all_percent_changes.append(abs(data['percent_change']))
            if data['std_dev'] is not None:
                all_std_devs.append(data['std_dev'])
    
    # Show only percentage-based metrics to avoid mixing different number bases
    col1, col2 = st.columns(2)
    
    with col1:
        if all_percent_changes:
            avg_percent = sum(all_percent_changes) / len(all_percent_changes)
            st.metric(
                label="Average Percent Change",
                value=format_percentage(avg_percent, 2),
                help="Average absolute percent change across all metrics (only shown for 2-file comparisons)"
            )
        else:
            st.metric(
                label="Average Percent Change",
                value="N/A",
                help="Percent change only available when comparing 2 files"
            )
    
    with col2:
        if all_std_devs:
            avg_std = sum(all_std_devs) / len(all_std_devs)
            st.metric(
                label="Average Variability (Std Dev)",
                value=format_number(avg_std, 2),
                help="Average standard deviation across all metrics (raw values, units vary by metric)"
            )
        else:
            st.metric(
                label="Average Variability (Std Dev)",
                value="N/A",
                help="Standard deviation requires at least 2 files"
            )

