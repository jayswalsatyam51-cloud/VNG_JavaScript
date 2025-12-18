"""
Domain models for VNG Data Analyzer
Core business entities and data structures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class MetricValue:
    """Represents a single metric value with its flag status"""
    value: float
    is_flagged: bool = False


@dataclass
class MetricData:
    """Represents metric data across multiple files"""
    values: List[float]
    flags: List[bool]
    delta: Optional[float] = None
    percent_change: Optional[float] = None
    std_dev: Optional[float] = None


@dataclass
class ParsedFile:
    """Represents a parsed VNG file"""
    name: str
    data: Dict[str, Dict[str, MetricValue]]  # {category: {metric: MetricValue}}
    uploaded_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0


@dataclass
class AnalysisResult:
    """Represents analysis results for a category"""
    category: str
    metrics: Dict[str, MetricData]  # {metric_name: MetricData}


@dataclass
class AnalysisResults:
    """Container for all analysis results"""
    results: Dict[str, AnalysisResult]  # {category: AnalysisResult}
    file_count: int
    total_metrics: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FileUploadInfo:
    """Information about uploaded files"""
    name: str
    size_bytes: int
    uploaded_at: datetime = field(default_factory=datetime.now)

