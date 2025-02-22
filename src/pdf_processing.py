from pdf2image import convert_from_path
import pytesseract

def extract_text_from_pdf(pdf_path):
    """Convertit un PDF en images et extrait le texte"""
    pages = convert_from_path(pdf_path, 300)  # Convertir en images à 300 DPI
    full_text = ""
    
    for page in pages:
        text = pytesseract.image_to_string(page, lang="fra")
        full_text += text.strip() + "\n\n"
    
    return full_text
