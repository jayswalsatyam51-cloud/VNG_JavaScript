"""
Analysis service for VNG data
"""

from typing import Dict, List, Any
from domain.models import ParsedFile, AnalysisResult, AnalysisResults, MetricData
from domain.exceptions import AnalysisError
from modules.analyzer import run_analysis as _run_analysis
from utils.statistics import calculate_std_dev, calculate_percent_change


class AnalysisService:
    """Service for analyzing VNG data"""
    
    @staticmethod
    def analyze_files(parsed_files: List[ParsedFile]) -> AnalysisResults:
        """
        Analyze multiple parsed files and return AnalysisResults
        
        Args:
            parsed_files: List of ParsedFile domain models
            
        Returns:
            AnalysisResults domain model
            
        Raises:
            AnalysisError: If analysis fails
        """
        try:
            if not parsed_files:
                return AnalysisResults(
                    results={},
                    file_count=0,
                    total_metrics=0
                )
            
            # Convert to legacy format for existing analyzer
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
            
            # Run analysis
            raw_results = _run_analysis(file_data_list)
            
            # Convert to domain models
            analysis_results: Dict[str, AnalysisResult] = {}
            total_metrics = 0
            
            for category, metrics_map in raw_results.items():
                metric_data_dict: Dict[str, MetricData] = {}
                for metric, data in metrics_map.items():
                    metric_data_dict[metric] = MetricData(
                        values=data['values'],
                        flags=data['flags'],
                        delta=data['delta'],
                        percent_change=data['percent_change'],
                        std_dev=data['std_dev']
                    )
                    total_metrics += 1
                
                analysis_results[category] = AnalysisResult(
                    category=category,
                    metrics=metric_data_dict
                )
            
            return AnalysisResults(
                results=analysis_results,
                file_count=len(parsed_files),
                total_metrics=total_metrics
            )
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {str(e)}") from e
    
    @staticmethod
    def analyze_files_dict(file_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze files using dictionary format (legacy compatibility)
        
        Args:
            file_data_list: List of file data dictionaries
            
        Returns:
            Dictionary with analysis results
        """
        return _run_analysis(file_data_list)

