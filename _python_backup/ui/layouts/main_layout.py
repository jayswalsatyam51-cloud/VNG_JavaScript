"""
Main layout structure with custom styling
"""

import streamlit as st


def apply_custom_styling():
    """Apply custom CSS styling to the application"""
    st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Success/Error messages */
    .stSuccess {
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 4px;
    }
    
    .stError {
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Info boxes */
    .stInfo {
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* File upload area */
    .uploadedFile {
        background-color: #f8f9fa;
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        background-color: #e9ecef;
        border-color: #0d6efd;
    }
    </style>
    """, unsafe_allow_html=True)

