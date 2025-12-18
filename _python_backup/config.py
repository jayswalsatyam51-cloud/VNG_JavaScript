"""
Backward compatibility layer for config
Imports from new config structure
"""

# Import from new config structure for backward compatibility
from config.constants import CHART_COLORS, MAX_METRICS_FOR_INTERPRETATION
from config.ui_config import (
    APP_TITLE, APP_SUBTITLE, UPLOAD_INSTRUCTIONS, UPLOAD_HELP,
    ANALYZE_BUTTON_TEXT, INTERPRET_BUTTON_TEXT, RESULTS_HEADER,
    CHART_INSTRUCTION, INTERPRETATION_SECTION_TITLE,
    INTERPRETATION_DESCRIPTION, INTERPRETATION_LOADING
)
from config.settings import settings

# For backward compatibility
AI_API_ENDPOINT = settings.AI_API_ENDPOINT
AI_API_BASE_URL = settings.AI_API_BASE_URL
AI_API_MODEL = settings.AI_API_MODEL
