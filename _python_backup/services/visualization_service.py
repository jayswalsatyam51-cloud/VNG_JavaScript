"""
Visualization service for creating charts
"""

from typing import Dict, List, Any, Tuple
import plotly.graph_objects as go
from modules.visualizer import render_line_chart as _render_line_chart
from modules.visualizer import render_category_chart as _render_category_chart
from domain.models import AnalysisResult, MetricData


class VisualizationService:
    """Service for creating visualizations"""
    
    @staticmethod
    def create_line_chart(
        metric_name: str,
        values: List[float],
        file_names: List[str]
    ) -> go.Figure:
        """
        Create a line chart for a metric
        
        Args:
            metric_name: Name of the metric
            values: List of values across files
            file_names: List of file names
            
        Returns:
            Plotly figure
        """
        return _render_line_chart(metric_name, values, file_names)
    
    @staticmethod
    def create_category_chart(
        category_name: str,
        metrics_map: Dict[str, MetricData],
        file_names: List[str],
        file_data_list: List[Dict[str, Any]]
    ) -> Tuple[go.Figure, bool]:
        """
        Create a category comparison chart
        
        Args:
            category_name: Name of the category
            metrics_map: Dictionary of metric data
            file_names: List of file names
            file_data_list: List of file data (for legacy compatibility)
            
        Returns:
            Tuple of (Plotly figure, show_disclaimer flag)
        """
        # Convert domain models to dict format for legacy function
        metrics_dict = {
            metric: {
                'values': data.values,
                'flags': data.flags,
                'delta': data.delta,
                'percent_change': data.percent_change,
                'std_dev': data.std_dev
            }
            for metric, data in metrics_map.items()
        }
        
        return _render_category_chart(
            category_name,
            metrics_dict,
            file_names,
            file_data_list
        )
    
    @staticmethod
    def create_line_chart_from_analysis(
        analysis_result: AnalysisResult,
        metric_name: str,
        file_names: List[str]
    ) -> go.Figure:
        """
        Create a line chart from analysis result
        
        Args:
            analysis_result: AnalysisResult domain model
            metric_name: Name of the metric to chart
            file_names: List of file names
            
        Returns:
            Plotly figure
        """
        if metric_name not in analysis_result.metrics:
            raise ValueError(f"Metric {metric_name} not found in category {analysis_result.category}")
        
        metric_data = analysis_result.metrics[metric_name]
        return _render_line_chart(metric_name, metric_data.values, file_names)

