import argparse
import os
import json
import uuid
from utils import list_files, ensure_directory_exists
from ocr import extract_text_from_image
from pdf_processing import extract_text_from_pdf
from text_processing import refine_ocr_results

OCR_ATTEMPTS = 10
SAVE_FOLDER = "training_test"

def process_files(folder):
    """Exécute l'OCR avec différents réglages et sauvegarde les résultats."""
    image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]
    pdf_extensions = [".pdf"]

    all_images = list_files(folder, image_extensions)
    all_pdfs = list_files(folder, pdf_extensions)

    ensure_directory_exists(SAVE_FOLDER)

    print(f"🔍 Détection : {len(all_images)} images et {len(all_pdfs)} PDFs trouvés\n")

    for file_path in all_images + all_pdfs:
        print(f"📄 Traitement du fichier : {file_path}")

        results = []
        for i in range(OCR_ATTEMPTS):
            print(f"📝 OCR Test {i+1}/{OCR_ATTEMPTS}...")
            text = extract_text_from_image(file_path) if file_path.endswith(tuple(image_extensions)) else extract_text_from_pdf(file_path)
            results.append(text)

        # 🔧 Amélioration du résultat
        optimized_text = refine_ocr_results(results)

        # 🎯 Génération d'un UID
        unique_id = str(uuid.uuid4())[:8]
        json_filename = os.path.join(SAVE_FOLDER, f"{os.path.basename(file_path)}_{unique_id}.json")

        # 📝 Sauvegarde des résultats
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump({"file": file_path, "ocr_attempts": OCR_ATTEMPTS, "optimized_text": optimized_text, "raw_results": results}, f, indent=4, ensure_ascii=False)

        print(f"✅ Résultat final optimisé enregistré dans {json_filename}\n{'-'*50}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TexTractor - OCR avec optimisation et apprentissage")
    parser.add_argument("--folder", type=str, required=True, help="Dossier contenant les fichiers à traiter")
    args = parser.parse_args()

    if not os.path.exists(args.folder):
        print(f"❌ Erreur : Dossier non trouvé : {args.folder}")
    else:
        process_files(args.folder)
