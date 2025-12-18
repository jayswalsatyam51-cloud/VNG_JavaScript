"""
Application settings and configuration
"""

import os
from typing import Optional


class Settings:
    """Application settings"""
    
    # AI API Configuration
    AI_API_BASE_URL: str = os.getenv(
        "AI_API_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta"
    )
    AI_API_MODEL: str = os.getenv("AI_API_MODEL", "gemini-2.5-flash-preview-09-2025")
    
    @property
    def AI_API_ENDPOINT(self) -> str:
        return f"{self.AI_API_BASE_URL}/models/{self.AI_API_MODEL}:generateContent"
    
    # AI Interpretation Settings
    MAX_METRICS_FOR_INTERPRETATION: int = int(
        os.getenv("MAX_METRICS_FOR_INTERPRETATION", "15")
    )
    
    # API Key (from secrets or environment)
    def get_api_key(self) -> Optional[str]:
        """Get API key from Streamlit secrets or environment"""
        try:
            import streamlit as st
            if 'AI_API_KEY' in st.secrets:
                return st.secrets['AI_API_KEY']
        except (ImportError, AttributeError):
            pass
        return os.getenv("AI_API_KEY")


# Global settings instance
settings = Settings()

