import cv2
import pytesseract
from PIL import Image
import json
import os
import random
import uuid
from utils import ensure_directory_exists
from train_ocr import load_best_configurations, save_best_configurations, mutate_score

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
PARAMS_FOLDER = "training_params"
ensure_directory_exists(PARAMS_FOLDER)

def mutate_ocr_config(config):
    """Modifie légèrement une configuration OCR pour tester des variantes"""
    config_parts = config.split(" ")
    
    if "--psm" in config_parts:
        psm_index = config_parts.index("--psm") + 1
        config_parts[psm_index] = str(random.choice([3, 4, 6, 7, 8, 11, 13]))

    return " ".join(config_parts)

def generate_new_ocr_configs():
    """Génère des paramètres OCR combinant exploitation et exploration"""
    base_configs = [
        "--psm 6",
        "--psm 11",
        "--psm 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "--psm 4 -c tessedit_char_blacklist=.,;:’",
        "--psm 8 -c oem=3"
    ]

    best_configs = load_best_configurations()
    weighted_configs = []
    
    for config, score in best_configs.items():
        weighted_configs.extend([mutate_ocr_config(config)] * int(score * 5))

    new_configs = [
        f"--psm {random.choice([3, 4, 6, 7, 8, 11, 13])} -c oem={random.choice([0, 1, 2, 3])}"
        for _ in range(5)
    ]

    return list(set(base_configs + weighted_configs + new_configs))

OCR_CONFIGURATIONS = generate_new_ocr_configs()

def preprocess_image(image_path):
    """Améliore dynamiquement l’image pour améliorer l’OCR"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    alpha = random.uniform(1.2, 2.0)
    beta = random.randint(0, 50)
    enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    processed = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    return processed

from text_processing import evaluate_ocr_result

def extract_text_from_image(image_path):
    """Extrait du texte en testant différentes configurations OCR améliorées."""
    processed_img = preprocess_image(image_path)
    results = {}
    scores = {}

    best_config_file = os.path.join(PARAMS_FOLDER, "best_config.json")
    if os.path.exists(best_config_file):
        with open(best_config_file, "r", encoding="utf-8") as f:
            best_config_data = json.load(f)
        best_config = best_config_data.get("best_config", OCR_CONFIGURATIONS[0])
        OCR_CONFIGURATIONS.insert(0, best_config)

    for config in OCR_CONFIGURATIONS:
        text = pytesseract.image_to_string(processed_img, lang="fra", config=config).strip()
        results[config] = text
        score = evaluate_ocr_result(image_path, text)
        scores[config] = score if score is not None else 0

    best_config = max(scores, key=scores.get)
    best_text = results[best_config]

    current_best_config = load_best_configurations()
    mutated_score = mutate_score(scores[best_config])

    if best_config in current_best_config:
        current_best_config[best_config] = max(current_best_config[best_config], mutated_score)
    else:
        current_best_config[best_config] = mutated_score

    save_best_configurations(current_best_config)

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
