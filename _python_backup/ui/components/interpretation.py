"""
Enhanced AI interpretation component
"""

import streamlit as st
import re
import json
from typing import Optional
from datetime import datetime
from io import BytesIO
from services.ai_service import AIService
from repositories.session_repository import SessionRepository
from config.settings import settings
from config.ui_config import (
    INTERPRETATION_SECTION_TITLE, INTERPRETATION_DESCRIPTION,
    INTERPRET_BUTTON_TEXT, INTERPRETATION_LOADING
)
from domain.exceptions import VNGError
from domain.models import AnalysisResults, AnalysisResult, MetricData


def render_interpretation_section():
    """Render enhanced AI interpretation section"""
    st.header(f"🤖 {INTERPRETATION_SECTION_TITLE}")
    st.write(INTERPRETATION_DESCRIPTION)
    
    # Get API key
    api_key = settings.get_api_key()
    
    if not api_key:
        st.warning("⚠️ AI API key not found. Please set it in `.streamlit/secrets.toml` or as environment variable `AI_API_KEY`.")
        st.code("""
# In .streamlit/secrets.toml:
AI_API_KEY = "your-api-key-here"
        """)
        return
    
    # Interpretation button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(INTERPRET_BUTTON_TEXT, type="primary"):
            get_interpretation()
    
    # Display interpretation if available
    interpretation_text = SessionRepository.get_interpretation_text()
    if interpretation_text:
        st.divider()
        st.subheader("📝 Interpretation Results")
        
        # Display in expandable sections
        with st.expander("View Full Interpretation", expanded=True):
            st.markdown(interpretation_text)
        
        # Copy button and text area
        st.subheader("📋 Copy & Download")
        
        # Clean text for copying (remove markdown formatting)
        clean_text = interpretation_text
        clean_text = re.sub(r'\*\*([^*]+?)\*\*', r'\1', clean_text)
        clean_text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'\1', clean_text)
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        
        copy_col1, copy_col2 = st.columns([1, 4])
        with copy_col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True, key="copy_btn"):
                # Store text in session state for JavaScript to access
                st.session_state.copy_text = clean_text
                st.session_state.trigger_copy = True
        
        # Show copyable text area
        with copy_col2:
            st.text_area(
                "Select and copy the text below (Ctrl+C / Cmd+C):",
                value=clean_text,
                height=100,
                key="copy_text_area",
                help="Click in the text area and press Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy"
            )
        
        # Execute copy JavaScript if triggered
        if st.session_state.get('trigger_copy', False):
            copy_to_clipboard(st.session_state.get('copy_text', ''))
            st.session_state.trigger_copy = False
            st.success("✅ Copied to clipboard!")
        
        # Export buttons with multiple format options
        st.subheader("📥 Download Interpretation")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Download as PDF (formatted document)
            try:
                pdf_content = format_interpretation_as_pdf(interpretation_text)
                st.download_button(
                    label="📑 Download as PDF",
                    data=pdf_content,
                    file_name=f"vng_interpretation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    help="Download as PDF - professionally formatted document"
                )
            except ImportError:
                st.info("💡 Install reportlab for PDF export: pip install reportlab")
            except Exception as e:
                st.error(f"PDF generation error: {str(e)}")
        
        with col2:
            # Download as Markdown (preserves formatting)
            markdown_content = format_interpretation_as_markdown(interpretation_text)
            st.download_button(
                label="📄 Download as Markdown",
                data=markdown_content,
                file_name=f"vng_interpretation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                help="Download as Markdown (.md) - preserves formatting, best for documentation"
            )
        
        with col3:
            # Download as HTML (formatted document)
            html_content = format_interpretation_as_html(interpretation_text)
            st.download_button(
                label="🌐 Download as HTML",
                data=html_content,
                file_name=f"vng_interpretation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                help="Download as HTML - formatted document that opens in any browser"
            )
        
        with col4:
            # Download as plain text (original option)
            st.download_button(
                label="📝 Download as Text",
                data=interpretation_text,
                file_name=f"vng_interpretation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="Download as plain text (.txt)"
            )


def get_interpretation():
    """Get AI interpretation of analysis results"""
    with st.spinner(INTERPRETATION_LOADING):
        try:
            # Get analysis results and convert to domain model
            analysis_results_dict = SessionRepository.get_analysis_results()
            file_data_list = SessionRepository.get_file_data_list()
            
            if not analysis_results_dict or not file_data_list:
                st.error("No analysis results available. Please analyze files first.")
                return
            
            # Convert to domain model for service
            results = {
                category: AnalysisResult(
                    category=category,
                    metrics={
                        metric: MetricData(
                            values=data['values'],
                            flags=data['flags'],
                            delta=data['delta'],
                            percent_change=data['percent_change'],
                            std_dev=data['std_dev']
                        )
                        for metric, data in metrics.items()
                    }
                )
                for category, metrics in analysis_results_dict.items()
            }
            
            analysis_results = AnalysisResults(
                results=results,
                file_count=len(file_data_list),
                total_metrics=sum(len(m) for m in analysis_results_dict.values())
            )
            
            # Get interpretation using service
            interpretation = AIService.get_interpretation(analysis_results)
            
            if interpretation:
                SessionRepository.set_interpretation_text(interpretation)
                st.success("Interpretation generated successfully!")
            else:
                st.error("Failed to get interpretation. Please try again.")
        except VNGError as e:
            st.error(f"Error getting interpretation: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")


def format_interpretation_as_markdown(interpretation_text: str) -> str:
    """
    Format interpretation text as a Markdown document with metadata
    
    Args:
        interpretation_text: The AI interpretation text
        
    Returns:
        Formatted Markdown document
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get file count for metadata
    file_data_list = SessionRepository.get_file_data_list()
    file_count = len(file_data_list) if file_data_list else 0
    
    markdown = f"""# VNG Test Interpretation Report

**Generated:** {timestamp}  
**Number of Files Analyzed:** {file_count}

---

## Clinical Interpretation

{interpretation_text}

---

*This report was generated by the VNG Analyzer application using AI-powered clinical interpretation.*
"""
    return markdown


def format_interpretation_as_html(interpretation_text: str) -> str:
    """
    Format interpretation text as an HTML document with styling
    
    Args:
        interpretation_text: The AI interpretation text
        
    Returns:
        Formatted HTML document
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get file count for metadata
    file_data_list = SessionRepository.get_file_data_list()
    file_count = len(file_data_list) if file_data_list else 0
    
    # Convert markdown-like formatting to HTML
    html_text = interpretation_text
    # Convert **bold** to <strong> (must do before italic to avoid conflicts)
    html_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_text)
    # Convert *italic* to <em> (only single asterisks not part of bold)
    html_text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', html_text)
    # Convert line breaks to paragraphs
    paragraphs = [p.strip() for p in html_text.split('\n\n') if p.strip()]
    html_body = '\n'.join([f'<p>{p}</p>' for p in paragraphs])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VNG Test Interpretation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .metadata {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
        .metadata strong {{
            color: #2c3e50;
        }}
        .content {{
            margin-top: 30px;
        }}
        .content p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        .content strong {{
            color: #2c3e50;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 0.9em;
            color: #7f8c8d;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>VNG Test Interpretation Report</h1>
        
        <div class="metadata">
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Number of Files Analyzed:</strong> {file_count}</p>
        </div>
        
        <h2>Clinical Interpretation</h2>
        <div class="content">
            {html_body}
        </div>
        
        <div class="footer">
            This report was generated by the VNG Analyzer application using AI-powered clinical interpretation.
        </div>
    </div>
</body>
</html>
"""
    return html


def clean_text_for_pdf(text: str) -> str:
    """
    Clean text for PDF generation by removing LaTeX commands,
    fixing malformed HTML, and converting markdown to HTML
    
    Args:
        text: Raw interpretation text
        
    Returns:
        Cleaned text with proper HTML tags for reportlab
    """
    # Step 1: Remove LaTeX commands like \text{...} (preserve content)
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    # Remove other LaTeX commands (but preserve content inside braces)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    # Remove standalone LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\s*', '', text)
    
    # Step 2: Remove ALL existing HTML tags first (we'll rebuild from markdown)
    # This ensures we start with clean text
    # Extract text content from HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Step 3: Clean up HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Step 4: Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Step 5: Convert markdown to HTML
    # Convert **bold** to <b> (handle nested cases - do this first)
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    # Convert *italic* to <i> (only single asterisks not part of bold)
    # Be careful not to match numbers or other single asterisks
    text = re.sub(r'(?<!\*)\*([^*\n\s][^*\n]*?[^*\n\s])\*(?!\*)', r'<i>\1</i>', text)
    
    # Clean up whitespace issues
    # Remove spaces between tags
    text = re.sub(r'>\s+<', '><', text)
    # Clean up any double spaces
    text = re.sub(r' +', ' ', text)
    # Remove spaces at start/end of tags
    text = re.sub(r'<([bi])>\s+', r'<\1>', text)
    text = re.sub(r'\s+</([bi])>', r'</\1>', text)
    
    # Ensure proper tag nesting and closure
    text = balance_html_tags(text)
    
    return text


def balance_html_tags(text: str) -> str:
    """
    Balance and properly nest HTML tags for reportlab compatibility
    
    Args:
        text: Text with HTML tags
        
    Returns:
        Text with properly balanced and nested tags
    """
    # Stack to track open tags
    tag_stack = []
    result = []
    i = 0
    
    while i < len(text):
        # Check for opening tag
        if text[i:i+3] == '<b>':
            tag_stack.append('b')
            result.append('<b>')
            i += 3
        elif text[i:i+3] == '<i>':
            tag_stack.append('i')
            result.append('<i>')
            i += 3
        # Check for closing tag
        elif text[i:i+4] == '</b>':
            # Close any open <i> tags before closing <b>
            while tag_stack and tag_stack[-1] == 'i':
                tag_stack.pop()
                result.append('</i>')
            if tag_stack and tag_stack[-1] == 'b':
                tag_stack.pop()
                result.append('</b>')
            else:
                # Unmatched closing tag, skip it
                pass
            i += 4
        elif text[i:i+4] == '</i>':
            if tag_stack and tag_stack[-1] == 'i':
                tag_stack.pop()
                result.append('</i>')
            else:
                # Unmatched closing tag, skip it
                pass
            i += 4
        else:
            result.append(text[i])
            i += 1
    
    # Close any remaining open tags in reverse order
    while tag_stack:
        tag = tag_stack.pop()
        result.append(f'</{tag}>')
    
    balanced_text = ''.join(result)
    
    # Final check: ensure no unclosed tags
    open_b = balanced_text.count('<b>')
    close_b = balanced_text.count('</b>')
    open_i = balanced_text.count('<i>')
    close_i = balanced_text.count('</i>')
    
    if open_b > close_b:
        balanced_text += '</b>' * (open_b - close_b)
    if open_i > close_i:
        balanced_text += '</i>' * (open_i - close_i)
    
    return balanced_text


def escape_html_for_pdf(text: str) -> str:
    """
    Escape HTML special characters for safe PDF rendering
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    # Remove all HTML tags first
    text = re.sub(r'<[^>]+>', '', text)
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def format_interpretation_as_pdf(interpretation_text: str) -> bytes:
    """
    Format interpretation text as a PDF document with professional styling
    
    Args:
        interpretation_text: The AI interpretation text
        
    Returns:
        PDF file as bytes
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
    except ImportError:
        raise ImportError("reportlab is required for PDF generation. Install it with: pip install reportlab")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get file count for metadata
    file_data_list = SessionRepository.get_file_data_list()
    file_count = len(file_data_list) if file_data_list else 0
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2c3e50',
        spaceAfter=30,
        alignment=TA_LEFT
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#34495e',
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Metadata style
    metadata_style = ParagraphStyle(
        'Metadata',
        parent=styles['BodyText'],
        fontSize=10,
        textColor='#555555',
        leftIndent=20,
        spaceAfter=6
    )
    
    # Footer style
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Italic'],
        fontSize=9,
        textColor='#7f8c8d',
        alignment=TA_LEFT
    )
    
    # Add title
    story.append(Paragraph("VNG Test Interpretation Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add metadata
    story.append(Paragraph(f"<b>Generated:</b> {timestamp}", metadata_style))
    story.append(Paragraph(f"<b>Number of Files Analyzed:</b> {file_count}", metadata_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add section heading
    story.append(Paragraph("Clinical Interpretation", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Process interpretation text
    # Clean and convert markdown-like formatting to HTML for reportlab
    pdf_text = clean_text_for_pdf(interpretation_text)
    
    # Split into paragraphs and add to story
    paragraphs = [p.strip() for p in pdf_text.split('\n\n') if p.strip()]
    for para in paragraphs:
        # Replace single line breaks with spaces for better formatting
        para = para.replace('\n', ' ')
        if para.strip():  # Only add non-empty paragraphs
            try:
                story.append(Paragraph(para, body_style))
                story.append(Spacer(1, 0.1*inch))
            except Exception as e:
                # If paragraph parsing fails, add as plain text
                # Escape HTML and add as plain text
                plain_text = escape_html_for_pdf(para)
                story.append(Paragraph(plain_text, body_style))
                story.append(Spacer(1, 0.1*inch))
    
    # Add footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "This report was generated by the VNG Analyzer application using AI-powered clinical interpretation.",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def copy_to_clipboard(text: str):
    """
    Copy text to clipboard using JavaScript
    
    Args:
        text: Text to copy to clipboard
    """
    # Clean the text - remove markdown formatting for plain text copy
    clean_text = text
    # Remove markdown bold
    clean_text = re.sub(r'\*\*([^*]+?)\*\*', r'\1', clean_text)
    # Remove markdown italic
    clean_text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'\1', clean_text)
    # Remove any HTML tags
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    # Clean up extra whitespace
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    
    # Escape the text properly for JavaScript JSON
    escaped_text = json.dumps(clean_text)
    
    # JavaScript code to copy to clipboard - runs after DOM is ready
    js_code = f"""
    <script>
    (function() {{
        function copyToClipboard() {{
            const text = {escaped_text};
            
            function performCopy(textToCopy) {{
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(textToCopy).then(function() {{
                        console.log('Text copied to clipboard successfully');
                        // Show visual feedback
                        const event = new CustomEvent('copySuccess');
                        window.dispatchEvent(event);
                    }}, function(err) {{
                        console.error('Clipboard API failed: ', err);
                        fallbackCopy(textToCopy);
                    }});
                }} else {{
                    fallbackCopy(textToCopy);
                }}
            }}
            
            function fallbackCopy(textToCopy) {{
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                textArea.style.position = 'fixed';
                textArea.style.left = '0';
                textArea.style.top = '0';
                textArea.style.width = '2em';
                textArea.style.height = '2em';
                textArea.style.padding = '0';
                textArea.style.border = 'none';
                textArea.style.outline = 'none';
                textArea.style.boxShadow = 'none';
                textArea.style.background = 'transparent';
                textArea.style.opacity = '0';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {{
                    const successful = document.execCommand('copy');
                    if (successful) {{
                        console.log('Text copied using fallback method');
                        const event = new CustomEvent('copySuccess');
                        window.dispatchEvent(event);
                    }} else {{
                        console.error('Fallback copy command returned false');
                    }}
                }} catch (err) {{
                    console.error('Fallback copy failed: ', err);
                }}
                
                document.body.removeChild(textArea);
            }}
            
            // Execute copy
            performCopy(text);
        }}
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', copyToClipboard);
        }} else {{
            // DOM is already ready
            setTimeout(copyToClipboard, 100);
        }}
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0)

