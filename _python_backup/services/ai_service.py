"""
AI interpretation service
"""

from typing import Dict, Optional
from domain.models import AnalysisResults
from domain.exceptions import VNGError
from modules.ai_interpreter import get_interpretation as _get_interpretation
from modules.ai_interpreter import build_interpretation_prompt
from config.settings import settings


class AIService:
    """Service for AI-powered interpretation"""
    
    @staticmethod
    def get_interpretation(analysis_results: AnalysisResults) -> Optional[str]:
        """
        Get AI interpretation of analysis results
        
        Args:
            analysis_results: AnalysisResults domain model
            
        Returns:
            Interpretation text or None if error
            
        Raises:
            VNGError: If API key is missing or request fails
        """
        api_key = settings.get_api_key()
        if not api_key:
            raise VNGError("AI API key not configured")
        
        # Convert domain model to dict format for legacy function
        results_dict = {
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
        
        try:
            return _get_interpretation(
                api_key,
                results_dict,
                analysis_results.file_count
            )
        except Exception as e:
            raise VNGError(f"Failed to get AI interpretation: {str(e)}") from e

