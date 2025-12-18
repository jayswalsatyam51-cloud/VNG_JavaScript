"""
Visualization module for VNG data
Creates interactive charts using Plotly
"""

import plotly.graph_objects as go
from typing import Dict, List, Tuple, Any
from utils.statistics import calculate_linear_regression, calculate_percent_change
from config.constants import CHART_COLORS


def render_line_chart(metric_name: str, values: List[float], file_names: List[str]) -> go.Figure:
    """
    Renders a LINE chart for a selected test (RAW values).
    Includes trendline if 3+ files.
    
    Args:
        metric_name: The name of the test (for the title)
        values: The array of values to plot
        file_names: List of file names for x-axis labels
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Main metric line
    fig.add_trace(go.Scatter(
        x=file_names,
        y=values,
        mode='lines+markers',
        name=metric_name,
        line=dict(color='rgba(59, 130, 246, 1)', width=2),
        marker=dict(color='rgba(59, 130, 246, 1)', size=8)
    ))
    
    # Trendline for 3+ files
    if len(values) >= 3:
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
        showlegend=len(values) >= 3,  # Only show legend if there's a trendline
        height=400
    )
    
    return fig


def render_category_chart(category_name: str, metrics_map: Dict[str, Dict[str, Any]], 
                         file_names: List[str], all_file_data_list: List[Dict]) -> Tuple[go.Figure, bool]:
    """
    Renders a CLUSTERED COLUMN chart for a selected category.
    If 1 file: shows raw values.
    If >1 file: shows PERCENT CHANGE from File 1.
    
    Args:
        category_name: The name of the category
        metrics_map: Dictionary of metrics for this category
        file_names: List of file names
        all_file_data_list: List of all file data (for accessing baseline values)
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    metric_names = sorted(metrics_map.keys())
    num_files = len(file_names)
    
    if num_files == 1:
        # --- LOGIC FOR 1 FILE (RAW VALUES) ---
        data_for_file = [metrics_map[metric]['values'][0] for metric in metric_names]
        
        fig.add_trace(go.Bar(
            x=metric_names,
            y=data_for_file,
            name=file_names[0],
            marker_color=CHART_COLORS[0]
        ))
        
        chart_title = f'Category: {category_name} (Raw Values)'
        y_axis_title = 'Raw Value'
        show_disclaimer = False
        
    else:
        # --- LOGIC FOR >1 FILE (% CHANGE) ---
        # We need one dataset per FILE (except File 1)
        for file_index in range(1, num_files):
            data_for_this_file = []
            
            # For each metric, get the % change from File 1
            for metric in metric_names:
                metric_data = metrics_map[metric]
                baseline = metric_data['values'][0]
                new_value = metric_data['values'][file_index]
                percent_change = calculate_percent_change(baseline, new_value)
                data_for_this_file.append(percent_change)
            
            color = CHART_COLORS[file_index % len(CHART_COLORS)]
            fig.add_trace(go.Bar(
                x=metric_names,
                y=data_for_this_file,
                name=f'{file_names[file_index]} (% Change)',
                marker_color=color
            ))
        
        chart_title = f'Category Comparison: {category_name} (% Change from File 1)'
        y_axis_title = 'Percent Change (%)'
        show_disclaimer = True
    
    fig.update_layout(
        title=chart_title,
        xaxis_title='Metric',
        yaxis_title=y_axis_title,
        barmode='group',  # Clustered bars
        hovermode='x unified',
        showlegend=num_files > 1,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
        height=400
    )
    
    return fig, show_disclaimer

