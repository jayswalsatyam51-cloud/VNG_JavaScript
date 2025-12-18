"""
AI interpretation module for VNG data
Integrates with AI API for clinical interpretation
"""

import requests
import time
from typing import Dict, Tuple, Optional
from config.settings import settings
from config.constants import MAX_METRICS_FOR_INTERPRETATION


def build_interpretation_prompt(results: Dict, num_files: int) -> Tuple[str, str]:
    """
    Constructs the system and user prompts for the AI API call.
    
    Args:
        results: The analysis results dictionary
        num_files: Number of files being compared
        
    Returns:
        Tuple of (system_prompt, user_query)
    """
    system_prompt = f"""Act as an expert clinical audiologist specializing in vestibular disorders. Your task is to provide a high-level clinical interpretation of VNG test data. The user will provide a summary of {num_files} tests. You must use web search to find normative data, test-retest reliability, and clinical significance for changes or variability in these specific VNG metrics.

Your response MUST follow this structure:
1.  **Executive Summary (TL;DR):** Start with a 2-3 sentence high-level summary of the most significant findings (e.g., "The main finding is a significant change in Saccades, while Pursuit tests remain stable.").
2.  **Detailed Analysis:**
    a. Acknowledge the number of tests being compared.
    b. For each metric, comment on the observed values.
    c. If a value is 'Flagged', note this and state that it was outside the normative range in that specific report.
    d. If 2 tests, comment on the 'change' (delta and percent change). Use web search to determine if this change is likely clinically significant or within normal test-retest reliability.
    e. If 3+ tests, comment on the 'variability' (standard deviation). Use web search to determine if this level of variability is high or low for this metric.
3.  **Overall Summary:** Synthesize all the detailed findings into a cohesive summary.
4.  **Disclaimer:** **Crucially, conclude with a clear disclaimer that this is not medical advice and a formal diagnosis requires a qualified healthcare professional.**"""

    data_string = ""
    count = 0
    
    # Limit to first N results to avoid overly long prompt
    for category, metrics_map in results.items():
        if count >= MAX_METRICS_FOR_INTERPRETATION:
            break
        data_string += f"\nCategory: '{category}'\n"
        for metric, data in metrics_map.items():
            if count >= MAX_METRICS_FOR_INTERPRETATION:
                break
            
            data_string += f"  - Test: '{metric}'\n"
            data_string += f"    - Values: [{', '.join(f'{v:.2f}' for v in data['values'])}]\n"
            
            # Add flag information
            flags = [f"File {i+1}: Flagged" for i, f in enumerate(data['flags']) if f]
            if flags:
                data_string += f"    - Flags: [{', '.join(flags)}]\n"
            
            if data['delta'] is not None:
                data_string += f"    - Abs. Change (Delta): {data['delta']:.2f}\n"
            if data['percent_change'] is not None:
                data_string += f"    - Perc. Change: {data['percent_change']:.2f}%\n"
            if data['std_dev'] is not None:
                data_string += f"    - Standard Deviation: {data['std_dev']:.2f}\n"
            count += 1
    
    if count >= MAX_METRICS_FOR_INTERPRETATION:
        data_string += "\n... and more ...\n"
    
    user_query = f"""I have analyzed {num_files} VNG reports. Here is a summary of the metrics that were common across all files:
{data_string}

Please provide a high-level clinical interpretation of these findings. Focus on whether the changes (for 2 tests) or variability (for 3+ tests) are clinically significant, using web search to find normative data and test-retest reliability for these specific VNG metrics. Pay attention to any 'Flagged' items, as these were outside normative ranges on the report."""
    
    return system_prompt, user_query


def get_interpretation(api_key: str, results: Dict, num_files: int) -> Optional[str]:
    """
    Calls the AI API for interpretation with retry logic.
    
    Args:
        api_key: AI API key
        results: The analysis results dictionary
        num_files: Number of files being compared
        
    Returns:
        The interpretation text, or None if error occurred
    """
    system_prompt, user_query = build_interpretation_prompt(results, num_files)
    
    api_url = f"{settings.AI_API_ENDPOINT}?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
    }
    
    # Implement exponential backoff for retries
    max_retries = 3
    delay = 1.0  # 1 second
    
    for retry in range(max_retries):
        try:
            response = requests.post(
                api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.ok:
                result = response.json()
                
                if (result.get('candidates') and 
                    result['candidates'][0].get('content') and
                    result['candidates'][0]['content'].get('parts') and
                    result['candidates'][0]['content']['parts'][0].get('text')):
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    raise ValueError("Invalid API response structure")
            
            # Retry on 5xx errors or 429 (Too Many Requests)
            if response.status_code >= 500 or response.status_code == 429:
                if retry < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    raise Exception(f"API Error: {response.status_code} {response.status_text} (Max retries reached)")
            else:
                # Don't retry on client errors like 400
                raise Exception(f"API Error: {response.status_code} {response.status_text}")
                
        except requests.exceptions.RequestException as e:
            if retry < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            else:
                raise Exception(f"Request failed: {str(e)}")
    
    return None

