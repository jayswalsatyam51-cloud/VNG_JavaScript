"""
Statistical analysis module for VNG data
Compares metrics across multiple files and calculates statistics
"""

from typing import Dict, List, Optional, Any
from utils.statistics import calculate_std_dev, calculate_percent_change


def run_analysis(file_data_list: List[Dict[str, Dict[str, Dict[str, Any]]]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Analyzes the data from multiple file maps.
    
    Args:
        file_data_list: List of dictionaries, each containing parsed file data
                       Format: [{'name': str, 'data': {category: {metric: {value, is_flagged}}}}]
    
    Returns:
        Nested dictionary with analysis results:
        {category: {metric: {values: [], flags: [], delta: float|None, 
                             std_dev: float|None, percent_change: float|None}}}
    """
    results: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    if not file_data_list or len(file_data_list) == 0:
        return results
    
    first_map = file_data_list[0]['data']
    
    # 1. Find common category:metric pairs ("Apples to Apples")
    # Build a set of all (category, metric) pairs from the first file
    common_pairs = set()
    for category, metrics in first_map.items():
        for metric in metrics.keys():
            common_pairs.add((category, metric))
    
    # Check which pairs exist in all files
    for file_data in file_data_list[1:]:
        file_pairs = set()
        for category, metrics in file_data['data'].items():
            for metric in metrics.keys():
                file_pairs.add((category, metric))
        # Keep only pairs that exist in this file too
        common_pairs = common_pairs.intersection(file_pairs)
    
    # 2. Populate results and calculate stats
    for category, metric in common_pairs:
        # Extract values and flags separately
        values = []
        flags = []
        
        for file_data in file_data_list:
            # Check if category and metric exist in this file
            if category in file_data['data'] and metric in file_data['data'][category]:
                metric_data = file_data['data'][category][metric]
                values.append(metric_data['value'])
                flags.append(metric_data['is_flagged'])
            else:
                # Skip this file if it doesn't have this metric
                continue
        
        # Only process if we have data from all files
        if len(values) != len(file_data_list):
            continue
        
        # Calculate statistics
        delta = None
        std_dev = None
        percent_change = None
        
        if len(file_data_list) == 2:
            delta = values[1] - values[0]
            percent_change = calculate_percent_change(values[0], values[1])
        
        if len(file_data_list) >= 2:
            std_dev = calculate_std_dev(values)
        
        # Ensure category exists in results
        if category not in results:
            results[category] = {}
        
        # Store metric data
        results[category][metric] = {
            'values': values,
            'flags': flags,
            'delta': delta,
            'std_dev': std_dev,
            'percent_change': percent_change
        }
    
    return results

