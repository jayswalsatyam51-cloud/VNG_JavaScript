"""
Session state repository
Manages Streamlit session state in a centralized way
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from domain.models import ParsedFile, AnalysisResults


class SessionRepository:
    """Repository for managing session state"""
    
    # Session state keys
    KEY_FILE_DATA_LIST = 'file_data_list'
    KEY_ANALYSIS_RESULTS = 'analysis_results'
    KEY_SELECTED_CATEGORY = 'selected_category'
    KEY_SELECTED_METRIC = 'selected_metric'
    KEY_INTERPRETATION_TEXT = 'interpretation_text'
    
    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        if SessionRepository.KEY_FILE_DATA_LIST not in st.session_state:
            st.session_state[SessionRepository.KEY_FILE_DATA_LIST] = []
        if SessionRepository.KEY_ANALYSIS_RESULTS not in st.session_state:
            st.session_state[SessionRepository.KEY_ANALYSIS_RESULTS] = None
        if SessionRepository.KEY_SELECTED_CATEGORY not in st.session_state:
            st.session_state[SessionRepository.KEY_SELECTED_CATEGORY] = None
        if SessionRepository.KEY_SELECTED_METRIC not in st.session_state:
            st.session_state[SessionRepository.KEY_SELECTED_METRIC] = None
        if SessionRepository.KEY_INTERPRETATION_TEXT not in st.session_state:
            st.session_state[SessionRepository.KEY_INTERPRETATION_TEXT] = None
    
    @staticmethod
    def get_file_data_list() -> List[Dict[str, Any]]:
        """Get list of parsed file data"""
        return st.session_state.get(SessionRepository.KEY_FILE_DATA_LIST, [])
    
    @staticmethod
    def set_file_data_list(data: List[Dict[str, Any]]):
        """Set list of parsed file data"""
        st.session_state[SessionRepository.KEY_FILE_DATA_LIST] = data
    
    @staticmethod
    def get_analysis_results() -> Optional[Dict[str, Any]]:
        """Get analysis results"""
        return st.session_state.get(SessionRepository.KEY_ANALYSIS_RESULTS)
    
    @staticmethod
    def set_analysis_results(results: Dict[str, Any]):
        """Set analysis results"""
        st.session_state[SessionRepository.KEY_ANALYSIS_RESULTS] = results
    
    @staticmethod
    def get_selected_category() -> Optional[str]:
        """Get selected category"""
        return st.session_state.get(SessionRepository.KEY_SELECTED_CATEGORY)
    
    @staticmethod
    def set_selected_category(category: Optional[str]):
        """Set selected category"""
        st.session_state[SessionRepository.KEY_SELECTED_CATEGORY] = category
    
    @staticmethod
    def get_selected_metric() -> Optional[str]:
        """Get selected metric"""
        return st.session_state.get(SessionRepository.KEY_SELECTED_METRIC)
    
    @staticmethod
    def set_selected_metric(metric: Optional[str]):
        """Set selected metric"""
        st.session_state[SessionRepository.KEY_SELECTED_METRIC] = metric
    
    @staticmethod
    def get_interpretation_text() -> Optional[str]:
        """Get interpretation text"""
        return st.session_state.get(SessionRepository.KEY_INTERPRETATION_TEXT)
    
    @staticmethod
    def set_interpretation_text(text: Optional[str]):
        """Set interpretation text"""
        st.session_state[SessionRepository.KEY_INTERPRETATION_TEXT] = text
    
    @staticmethod
    def clear_selection():
        """Clear selected category and metric"""
        st.session_state[SessionRepository.KEY_SELECTED_CATEGORY] = None
        st.session_state[SessionRepository.KEY_SELECTED_METRIC] = None
    
    @staticmethod
    def clear_interpretation():
        """Clear interpretation text"""
        st.session_state[SessionRepository.KEY_INTERPRETATION_TEXT] = None

