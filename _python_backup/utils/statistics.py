"""
Statistical helper functions for VNG data analysis
"""

import numpy as np
from typing import List, Optional


def calculate_std_dev(values: List[float]) -> float:
    """
    Calculates the standard deviation of an array of numbers (sample standard deviation).
    
    Args:
        values: Array of numbers
        
    Returns:
        The standard deviation (0 if less than 2 values)
    """
    if len(values) < 2:
        return 0.0
    
    return float(np.std(values, ddof=1))  # ddof=1 for sample standard deviation


def calculate_percent_change(baseline: float, new_value: float) -> Optional[float]:
    """
    Calculates the percent change from baseline to new value.
    Handles division by zero cases.
    
    Args:
        baseline: The File 1 value (baseline)
        new_value: The current file's value
        
    Returns:
        The percent change, or None if N/A (e.g., baseline is 0 and new_value is not 0)
    """
    if baseline == 0:
        # 0->0 is 0% change. 0->5 is Inf change (skip)
        return 0.0 if new_value == 0 else None
    
    if baseline is None or new_value is None:
        return None
    
    return ((new_value - baseline) / baseline) * 100


def calculate_linear_regression(y_values: List[float]) -> List[float]:
    """
    Calculates a simple linear regression trendline.
    
    Args:
        y_values: Array of Y-axis values
        
    Returns:
        Array of Y-values for the trendline
    """
    n = len(y_values)
    if n < 2:
        return []
    
    # Create x values [0, 1, 2, ...]
    x_values = list(range(n))
    
    # Filter out None/null values
    valid_points = [(x, y) for x, y in zip(x_values, y_values) 
                    if y is not None and not np.isnan(y)]
    
    if len(valid_points) < 2:
        return [None] * n
    
    # Calculate sums
    sum_x = sum(p[0] for p in valid_points)
    sum_y = sum(p[1] for p in valid_points)
    sum_xy = sum(p[0] * p[1] for p in valid_points)
    sum_xx = sum(p[0] * p[0] for p in valid_points)
    
    vn = len(valid_points)
    
    # Calculate slope and intercept
    denominator = vn * sum_xx - sum_x * sum_x
    if denominator == 0:
        # Vertical line - unlikely but handle it
        slope = 0
        intercept = sum_y / vn
    else:
        slope = (vn * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / vn
    
    # Generate trendline values
    return [slope * x + intercept for x in x_values]

