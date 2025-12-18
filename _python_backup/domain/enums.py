"""
Domain enumerations
"""

from enum import Enum


class ChartType(str, Enum):
    """Types of charts available"""
    LINE = "line"
    BAR = "bar"
    HEATMAP = "heatmap"
    RADAR = "radar"
    BOX = "box"


class AnalysisStatus(str, Enum):
    """Status of analysis operation"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class MetricChangeType(str, Enum):
    """Type of change in metric value"""
    IMPROVED = "improved"
    DECLINED = "declined"
    STABLE = "stable"
    UNKNOWN = "unknown"

