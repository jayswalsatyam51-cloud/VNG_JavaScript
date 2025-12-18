"""
VNG text file parsing module
Converts raw VNG report text into structured data
"""

import re
from typing import Dict, Any


def parse_vng_text(text: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Parses the raw text of a VNG file into a structured dictionary.
    
    Args:
        text: The raw text content of the .txt file
        
    Returns:
        A nested dictionary where:
        - Outer key: category name (e.g., "Saccades")
        - Inner key: metric name (e.g., "Latency")
        - Value: dict with 'value' (float) and 'is_flagged' (bool)
        
        Structure: {category: {metric: {value: float, is_flagged: bool}}}
    """
    data_map: Dict[str, Dict[str, Dict[str, Any]]] = {}
    current_category = "General"
    lines = text.split('\n')
    
    # Regex pattern to match: "Metric Name: 123.45 | FLAG" or "Metric Name: 123.45"
    value_regex = re.compile(r': ([\d.-]+)[\s%a-zA-Z]*?(\| FLAG)?$')
    
    for line in lines:
        trimmed_line = line.strip()
        if not trimmed_line:
            continue
        
        match = value_regex.search(trimmed_line)
        
        if match and match.group(1):
            try:
                value = float(match.group(1))
            except ValueError:
                continue
            
            # Check if the flag exists
            is_flagged = match.group(2) is not None
            
            # Extract metric name (everything before the colon, minus any trailing parentheses)
            metric_name = trimmed_line[:trimmed_line.rindex(':')].strip()
            metric_name = re.sub(r'\s*\([^)]+\)$', '', metric_name).strip()
            
            # Ensure category exists in data_map
            if current_category not in data_map:
                data_map[current_category] = {}
            
            # Store the metric data
            data_map[current_category][metric_name] = {
                'value': value,
                'is_flagged': is_flagged
            }
            
        elif trimmed_line.endswith(':') and not value_regex.search(trimmed_line):
            # This line is a new category (ends with colon and doesn't match value pattern)
            if not trimmed_line.startswith('Summary of Flagged Findings'):
                current_category = trimmed_line[:-1].strip()
                # Handle section headers like "VISUOMOTOR //"
                if current_category.endswith(' //'):
                    current_category = current_category[:-3].strip()
    
    return data_map

