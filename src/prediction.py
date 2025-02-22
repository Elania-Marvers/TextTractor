import os
import json
from utils import list_files

TRAINING_FOLDER = "training_test"

def analyze_all_results():
    """Parcourt tous les fichiers JSON et affiche les prédictions finales optimisées"""
    json_files = list_files(TRAINING_FOLDER, extensions=[".json"])

    print(f"🔍 {len(json_files)} fichiers OCR analysés\n")

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"📜 Fichier: {data['file']}")
        print(f"🔎 Texte final optimisé:\n{data['optimized_text']}\n{'-'*50}")

if __name__ == "__main__":
    analyze_all_results()
