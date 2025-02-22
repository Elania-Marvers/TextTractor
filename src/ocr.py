import cv2
import pytesseract
from PIL import Image
import json
import os
import random
import uuid
from utils import ensure_directory_exists

# 📍 Chemin vers Tesseract
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# 📁 Dossier pour sauvegarder les tests
PARAMS_FOLDER = "training_params"
ensure_directory_exists(PARAMS_FOLDER)

def generate_new_ocr_configs():
    """Génère dynamiquement de nouveaux paramètres OCR basés sur les précédents avec des variations aléatoires."""
    
    base_configs = [
        "--psm 6",
        "--psm 11",
        "--psm 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "--psm 4 -c tessedit_char_blacklist=.,;:’",
        "--psm 8 -c oem=3"
    ]

    # Générer de nouvelles combinaisons aléatoires
    new_configs = []
    for _ in range(3):  # Ajouter 3 configurations aléatoires
        psm_mode = random.choice([3, 4, 6, 7, 8, 11, 13])
        whitelist = "".join(random.sample("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", random.randint(10, 26)))
        blacklist = "".join(random.sample(".,;:’", random.randint(1, 4)))
        oem = random.choice([0, 1, 2, 3])
        
        new_config = f"--psm {psm_mode} -c tessedit_char_whitelist={whitelist} -c tessedit_char_blacklist={blacklist} -c oem={oem}"
        new_configs.append(new_config)

    return base_configs + new_configs

# 🛠️ Génération dynamique des configurations testées
OCR_CONFIGURATIONS = generate_new_ocr_configs()

def preprocess_image(image_path):
    """Prépare l'image pour l'OCR (grayscale + binarisation)"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    return processed

def score_text(text):
    """Attribue un score à un texte basé sur la lisibilité"""
    words = text.split()
    return len(words) + sum(1 for word in words if len(word) > 3)  # Bonus pour les mots longs

from text_processing import evaluate_ocr_result

def extract_text_from_image(image_path):
    """Extrait du texte depuis une image avec des configurations OCR améliorées."""
    processed_img = preprocess_image(image_path)

    results = {}
    scores = {}

    # Charger le meilleur paramètre enregistré
    best_config_file = os.path.join(PARAMS_FOLDER, "best_config.json")
    if os.path.exists(best_config_file):
        with open(best_config_file, "r", encoding="utf-8") as f:
            best_config_data = json.load(f)
        best_config = best_config_data.get("best_config", OCR_CONFIGURATIONS[0])
        OCR_CONFIGURATIONS.insert(0, best_config)  # Priorité au meilleur paramètre

    for config in OCR_CONFIGURATIONS:
        text = pytesseract.image_to_string(processed_img, lang="fra", config=config).strip()
        results[config] = text
        score = evaluate_ocr_result(image_path, text)
        scores[config] = score if score is not None else 0

    # 🔍 Sélection de la meilleure configuration (pondérée par le score)
    best_config = max(scores, key=scores.get)
    best_text = results[best_config]

    # 📝 Sauvegarde des paramètres testés
    uid = str(uuid.uuid4())[:8]
    param_file = os.path.join(PARAMS_FOLDER, f"{os.path.basename(image_path)}_{uid}.json")
    with open(param_file, "w", encoding="utf-8") as f:
        json.dump({
            "file": image_path,
            "tested_configs": results,
            "scores": scores,
            "best_config": best_config,
            "best_text": best_text
        }, f, indent=4, ensure_ascii=False)

    print(f"✅ OCR terminé : {image_path} | Meilleure config : {best_config} (Score: {scores[best_config]:.2f})")
    return best_text

