"""
Enhanced file upload component
"""

import streamlit as st
from typing import List, Any
from services.file_service import FileService
from utils.formatters import format_file_size
from domain.exceptions import ValidationError, FileError


def render_file_upload_section() -> List[Any]:
    """
    Render enhanced file upload section with drag-and-drop styling
    
    Returns:
        List of uploaded files or None
    """
    st.subheader("📤 Upload VNG Reports")
    
    # Custom styling for drag-and-drop area
    st.markdown("""
    <style>
    .uploadedFile {
        background-color: #f0f2f6;
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drag and drop your VNG report files here, or click to browse",
        type=['txt'],
        accept_multiple_files=True,
        help="Upload one or more .txt VNG report files for analysis"
    )
    
    # Display uploaded files with metadata
    if uploaded_files:
        st.write("**📋 Uploaded Files:**")
        
        for idx, file in enumerate(uploaded_files, 1):
            try:
                file_info = FileService.get_file_info(file)
                
                with st.expander(f"📄 {file_info.name} ({format_file_size(file_info.size_bytes)})", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Validate file
                        try:
                            FileService.validate_file(file.name, len(file.getvalue()))
                            st.success("✓ Valid file")
                        except ValidationError as e:
                            st.error(f"✗ {str(e)}")
                    
                    with col2:
                        # File preview button
                        if st.button("👁️ Preview", key=f"preview_{idx}"):
                            st.session_state[f'preview_file_{idx}'] = not st.session_state.get(f'preview_file_{idx}', False)
                    
                    with col3:
                        # File info
                        st.caption(f"Size: {format_file_size(file_info.size_bytes)}")
                    
                    # File preview
                    if st.session_state.get(f'preview_file_{idx}', False):
                        try:
                            # Reset file pointer and read content
                            file.seek(0)
                            file_content = file.read().decode('utf-8')
                            preview_text = file_content[:2000] + ("..." if len(file_content) > 2000 else "")
                            st.text_area(
                                "File Contents",
                                value=preview_text,
                                height=200,
                                key=f"preview_content_{idx}",
                                disabled=True
                            )
                            # Reset file pointer again for later use
                            file.seek(0)
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
            except Exception as e:
                st.error(f"Error processing file {file.name}: {str(e)}")
    
    return uploaded_files

