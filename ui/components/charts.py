"""
Enhanced chart components with additional visualization types
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import pandas as pd
from modules.visualizer import render_line_chart, render_category_chart
from config.constants import CHART_COLORS


def render_heatmap(
    analysis_results: Dict[str, Any],
    file_data_list: List[Dict]
) -> go.Figure:
    """
    Render heatmap showing all metrics across all files
    
    Args:
        analysis_results: Analysis results dictionary
        file_data_list: List of file data
        
    Returns:
        Plotly figure
    """
    # Prepare data for heatmap
    metrics_list = []
    files_list = [f['name'] for f in file_data_list]
    values_matrix = []
    
    for category in sorted(analysis_results.keys()):
        for metric in sorted(analysis_results[category].keys()):
            metrics_list.append(f"{category}: {metric}")
            values = analysis_results[category][metric]['values']
            values_matrix.append(values)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=values_matrix,
        x=files_list,
        y=metrics_list,
        colorscale='Viridis',
        colorbar=dict(title="Value"),
        hovertemplate='File: %{x}<br>Metric: %{y}<br>Value: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Heatmap: All Metrics Across All Files',
        xaxis_title='File',
        yaxis_title='Metric',
        height=max(400, len(metrics_list) * 20),
        yaxis=dict(tickmode='linear', tickangle=-45)
    )
    
    return fig


def render_radar_chart(
    analysis_results: Dict[str, Any],
    file_data_list: List[Dict],
    category: str,
    selected_metrics: Optional[List[str]] = None
) -> go.Figure:
    """
    Render radar/spider chart for comparing metrics across files
    
    Args:
        analysis_results: Analysis results dictionary
        file_data_list: List of file data
        category: Category to visualize
        selected_metrics: Optional list of specific metrics to include
        
    Returns:
        Plotly figure
    """
    if category not in analysis_results:
        raise ValueError(f"Category {category} not found")
    
    category_metrics = analysis_results[category]
    all_metrics = selected_metrics if selected_metrics else sorted(category_metrics.keys())
    
    # Filter out metrics with no data (all zeros or missing)
    metrics_with_data = []
    for metric in all_metrics:
        if metric in category_metrics:
            values = category_metrics[metric]['values']
            # Check if metric has any non-zero, non-None data
            if values and any(v is not None and v != 0 for v in values):
                metrics_with_data.append(metric)
    
    if not metrics_with_data:
        raise ValueError(f"No metrics with data found in category {category}")
    
    metrics = metrics_with_data
    
    # Normalize values for radar chart (0-100 scale)
    fig = go.Figure()
    
    for file_idx, file_data in enumerate(file_data_list):
        values = []
        for metric in metrics:
            if metric in category_metrics:
                raw_value = category_metrics[metric]['values'][file_idx]
                values.append(raw_value)
            else:
                values.append(0)
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name=file_data['name'],
            line_color=CHART_COLORS[file_idx % len(CHART_COLORS)]
        ))
    
    # Calculate max value for range
    max_val = 0
    for metric in metrics:
        if metric in category_metrics:
            max_val = max(max_val, max(category_metrics[metric]['values']))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max_val, 100)]
            )),
        showlegend=True,
        title=f'Radar Chart: {category}',
        height=500
    )
    
    return fig


def render_enhanced_line_chart(
    metric_name: str,
    values: List[float],
    file_names: List[str],
    flags: Optional[List[bool]] = None,
    show_confidence: bool = False
) -> go.Figure:
    """
    Enhanced line chart with flagged value indicators and optional confidence intervals
    
    Args:
        metric_name: Name of the metric
        values: List of values
        file_names: List of file names
        flags: Optional list of flag indicators
        show_confidence: Whether to show confidence intervals
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Main line
    fig.add_trace(go.Scatter(
        x=file_names,
        y=values,
        mode='lines+markers',
        name=metric_name,
        line=dict(color='rgba(59, 130, 246, 1)', width=3),
        marker=dict(
            color=['red' if (flags and flags[i]) else 'rgba(59, 130, 246, 1)' 
                   for i in range(len(values))],
            size=10,
            symbol=['x' if (flags and flags[i]) else 'circle' for i in range(len(values))]
        )
    ))
    
    # Add annotations for flagged values
    if flags:
        for i, (val, is_flag) in enumerate(zip(values, flags)):
            if is_flag:
                fig.add_annotation(
                    x=file_names[i],
                    y=val,
                    text="⚠️",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="red",
                    ax=0,
                    ay=-30
                )
    
    # Add confidence intervals if requested and 3+ files
    if show_confidence and len(values) >= 3:
        import numpy as np
        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)
        upper_bound = [mean_val + 1.96 * std_val] * len(values)
        lower_bound = [mean_val - 1.96 * std_val] * len(values)
        
        # Add upper bound
        fig.add_trace(go.Scatter(
            x=file_names,
            y=upper_bound,
            mode='lines',
            name='Upper 95% CI',
            line=dict(width=0),
            showlegend=False
        ))
        
        # Add lower bound
        fig.add_trace(go.Scatter(
            x=file_names,
            y=lower_bound,
            mode='lines',
            name='Lower 95% CI',
            line=dict(width=0),
            fillcolor='rgba(59, 130, 246, 0.2)',
            fill='tonexty',
            showlegend=True
        ))
    
    # Add trendline if 3+ files
    if len(values) >= 3:
        from utils.statistics import calculate_linear_regression
        trendline_data = calculate_linear_regression(values)
        fig.add_trace(go.Scatter(
            x=file_names,
            y=trendline_data,
            mode='lines',
            name=f'{metric_name} (Trend)',
            line=dict(color='rgba(59, 130, 246, 1)', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=f'{metric_name} (Raw Values)',
        xaxis_title='File',
        yaxis_title='Raw Value',
        hovermode='x unified',
        showlegend=len(values) >= 3,
        height=450
    )
    
    return fig


def render_box_plot(
    analysis_results: Dict[str, Any],
    file_data_list: List[Dict],
    category: str,
    metric: str
) -> go.Figure:
    """
    Render box plot showing distribution and outliers for a metric with 3+ files
    
    Args:
        analysis_results: Analysis results dictionary
        file_data_list: List of file data
        category: Category name
        metric: Metric name
        
    Returns:
        Plotly figure
    """
    if category not in analysis_results or metric not in analysis_results[category]:
        raise ValueError(f"Metric {metric} not found in category {category}")
    
    values = analysis_results[category][metric]['values']
    
    if len(values) < 3:
        raise ValueError("Box plot requires at least 3 files")
    
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=values,
        name=metric,
        boxmean='sd',  # Show mean and standard deviation
        marker_color='rgba(59, 130, 246, 0.7)',
        line=dict(color='rgba(59, 130, 246, 1)', width=2)
    ))
    
    fig.update_layout(
        title=f'Box Plot: {metric} (Distribution)',
        yaxis_title='Value',
        xaxis_title='Metric',
        height=450,
        showlegend=False
    )
    
    return fig


def render_correlation_matrix(
    analysis_results: Dict[str, Any],
    category: str
) -> go.Figure:
    """
    Render correlation matrix showing relationships between metrics in a category
    
    Args:
        analysis_results: Analysis results dictionary
        category: Category to analyze
        
    Returns:
        Plotly figure
    """
    if category not in analysis_results:
        raise ValueError(f"Category {category} not found")
    
    category_metrics = analysis_results[category]
    
    if len(category_metrics) < 2:
        raise ValueError("Correlation matrix requires at least 2 metrics")
    
    # Prepare data for correlation
    metric_names = []
    values_matrix = []
    
    for metric in sorted(category_metrics.keys()):
        metric_names.append(metric)
        values_matrix.append(category_metrics[metric]['values'])
    
    # Calculate correlation matrix
    import numpy as np
    df = pd.DataFrame(values_matrix, index=metric_names).T
    corr_matrix = df.corr().values
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=metric_names,
        y=metric_names,
        colorscale='RdBu',
        zmid=0,
        colorbar=dict(title="Correlation"),
        hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>',
        text=[[f'{val:.2f}' for val in row] for row in corr_matrix],
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=f'Correlation Matrix: {category}',
        xaxis_title='Metric',
        yaxis_title='Metric',
        height=500,
        xaxis=dict(tickangle=-45),
        yaxis=dict(tickangle=0)
    )
    
    return fig


def render_multi_metric_comparison(
    analysis_results: Dict[str, Any],
    file_data_list: List[Dict],
    category: str,
    selected_metrics: List[str]
) -> go.Figure:
    """
    Render line chart comparing multiple metrics on the same chart
    
    Args:
        analysis_results: Analysis results dictionary
        file_data_list: List of file data
        category: Category name
        selected_metrics: List of metric names to compare
        
    Returns:
        Plotly figure
    """
    if category not in analysis_results:
        raise ValueError(f"Category {category} not found")
    
    category_metrics = analysis_results[category]
    file_names = [f['name'] for f in file_data_list]
    
    fig = go.Figure()
    
    for idx, metric in enumerate(selected_metrics):
        if metric not in category_metrics:
            continue
        
        values = category_metrics[metric]['values']
        color = CHART_COLORS[idx % len(CHART_COLORS)]
        
        fig.add_trace(go.Scatter(
            x=file_names,
            y=values,
            mode='lines+markers',
            name=metric,
            line=dict(color=color, width=2),
            marker=dict(color=color, size=8)
        ))
    
    fig.update_layout(
        title=f'Multi-Metric Comparison: {category}',
        xaxis_title='File',
        yaxis_title='Value',
        hovermode='x unified',
        showlegend=True,
        height=500,
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5)
    )
    
    return fig


def render_enhanced_bar_chart(
    category_name: str,
    metrics_map: Dict[str, Dict[str, Any]],
    file_names: List[str],
    orientation: str = 'vertical',
    stacked: bool = False,
    show_gradients: bool = False
) -> go.Figure:
    """
    Enhanced bar chart with options for horizontal, stacked, and color gradients
    
    Args:
        category_name: Category name
        metrics_map: Dictionary of metrics
        file_names: List of file names
        orientation: 'vertical' or 'horizontal'
        stacked: Whether to stack bars
        show_gradients: Whether to use color gradients based on change magnitude
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    metric_names = sorted(metrics_map.keys())
    num_files = len(file_names)
    
    if num_files == 1:
        data_for_file = [metrics_map[metric]['values'][0] for metric in metric_names]
        
        if show_gradients:
            # Create gradient colors based on values
            max_val = max(data_for_file) if data_for_file else 1
            colors = [f'rgba(59, 130, 246, {0.3 + 0.7 * (val / max_val)})' for val in data_for_file]
        else:
            colors = CHART_COLORS[0]
        
        if orientation == 'horizontal':
            fig.add_trace(go.Bar(
                y=metric_names,
                x=data_for_file,
                name=file_names[0],
                marker_color=colors,
                orientation='h'
            ))
        else:
            fig.add_trace(go.Bar(
                x=metric_names,
                y=data_for_file,
                name=file_names[0],
                marker_color=colors
            ))
    else:
        # Multiple files - show percent change
        from utils.statistics import calculate_percent_change
        
        for file_index in range(1, num_files):
            data_for_this_file = []
            
            for metric in metric_names:
                metric_data = metrics_map[metric]
                baseline = metric_data['values'][0]
                new_value = metric_data['values'][file_index]
                percent_change = calculate_percent_change(baseline, new_value)
                data_for_this_file.append(percent_change if percent_change is not None else 0)
            
            color = CHART_COLORS[file_index % len(CHART_COLORS)]
            
            if orientation == 'horizontal':
                fig.add_trace(go.Bar(
                    y=metric_names,
                    x=data_for_this_file,
                    name=f'{file_names[file_index]} (% Change)',
                    marker_color=color,
                    orientation='h'
                ))
            else:
                fig.add_trace(go.Bar(
                    x=metric_names,
                    y=data_for_this_file,
                    name=f'{file_names[file_index]} (% Change)',
                    marker_color=color
                ))
    
    barmode = 'stack' if stacked else 'group'
    y_axis_title = 'Percent Change (%)' if num_files > 1 else 'Raw Value'
    
    fig.update_layout(
        title=f'Category: {category_name}',
        xaxis_title='Metric' if orientation == 'vertical' else y_axis_title,
        yaxis_title=y_axis_title if orientation == 'vertical' else 'Metric',
        barmode=barmode,
        hovermode='x unified',
        showlegend=num_files > 1,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
        height=500 if orientation == 'horizontal' else 400
    )
    
    return fig

