import os
import requests
import tempfile
import google.generativeai as genai
from pathlib import Path

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def process_image(image_url, caption=""):
    """
    Gemini Vision for image analysis
    """
    # Download image to RAM
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    
    # Gemini Vision API
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Upload image
    img_part = {
        "mime_type": "image/jpeg",
        "data": response.content
    }
    
    prompt = f"""Analyze this technical image.

CAPTION: {caption}

TASK:
- If chart/plot: extract data, axes, legends
- If diagram: describe architecture, flows
- If equation: transcribe to LaTeX
- If code screenshot: extract code

Format: Structured Markdown with headers and bullets."""

    result = model.generate_content([prompt, img_part])
    
    return f"# Image Analysis\n\n{result.text}\n\n**Caption**: {caption}"

def process_pdf(pdf_url):
    """
    Gemini File API for PDFs
    """
    # Download PDF to temp file
    response = requests.get(pdf_url, timeout=60)
    response.raise_for_status()
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name
    
    try:
        # Upload to Gemini
        uploaded_file = genai.upload_file(tmp_path)
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = """Create a complete reading note for this document:

1. **Document Type** (Paper, Report, Thesis, etc.)
2. **Metadata** (Authors, Date, Institution)
3. **Problem Statement** (1-2 sentences)
4. **Methodology** (approach, tools, datasets)
5. **Key Results** (quantitative if possible)
6. **Contributions** (scientific novelty)
7. **Limitations** (what is NOT addressed)
8. **Key Equations/Formulas** (if applicable, in LaTeX)

Format: Structured Markdown."""

        result = model.generate_content([prompt, uploaded_file])
        
        return result.text
    
    finally:
        # Cleanup
        Path(tmp_path).unlink()
        try:
            genai.delete_file(uploaded_file.name)
        except:
            pass
