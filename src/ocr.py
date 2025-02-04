import cv2
import pytesseract
from PIL import Image

# Configuration de Tesseract (chemin à adapter si nécessaire)
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

def preprocess_image(image_path):
    """Prépare l'image pour l'OCR (grayscale + binarisation)"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    return processed

def extract_text_from_image(image_path):
    """Extrait du texte depuis une image"""
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img, lang="fra")
    return text
