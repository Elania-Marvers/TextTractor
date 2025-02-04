import argparse
import os
from utils import list_files
from ocr import extract_text_from_image
from pdf_processing import extract_text_from_pdf

def process_files(folder):
    """Gère l'extraction de texte pour tous les fichiers du dossier"""
    image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]
    pdf_extensions = [".pdf"]
    
    all_images = list_files(folder, image_extensions)
    all_pdfs = list_files(folder, pdf_extensions)

    print(f"🔍 Détection : {len(all_images)} images et {len(all_pdfs)} PDFs trouvés dans {folder}\n")
    
    for img in all_images:
        print(f"📸 Traitement de l'image : {img}")
        text = extract_text_from_image(img)
        print("Texte extrait :\n", text, "\n" + "-"*50)
    
    for pdf in all_pdfs:
        print(f"📄 Traitement du PDF : {pdf}")
        text = extract_text_from_pdf(pdf)
        print("Texte extrait :\n", text, "\n" + "-"*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TexTractor - Extraction OCR avancée")
    parser.add_argument("--folder", type=str, required=True, help="Dossier contenant les fichiers à traiter")
    args = parser.parse_args()

    if not os.path.exists(args.folder):
        print("❌ Erreur : Dossier non trouvé :", args.folder)
    else:
        process_files(args.folder)
