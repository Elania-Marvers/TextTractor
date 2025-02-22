import os
import json
import random
from utils import list_files

PARAMS_FOLDER = "training_params"
BEST_CONFIG_FILE = os.path.join(PARAMS_FOLDER, "best_configurations.json")

def save_best_configurations(best_configs):
    """Stocke les meilleures configurations OCR avec leur score moyen."""
    with open(BEST_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(best_configs, f, indent=4, ensure_ascii=False)

def load_best_configurations():
    """Charge les meilleures configurations OCR enregistrées."""
    if os.path.exists(BEST_CONFIG_FILE):
        with open(BEST_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def mutate_score(score):
    """Ajoute un facteur aléatoire contrôlé pour éviter la stagnation des configurations"""
    mutation_factor = random.uniform(0.90, 1.10)  # Varie légèrement le score de ±10%
    return score * mutation_factor

def analyze_best_configs():
    """Analyse et optimise les paramètres OCR basés sur les scores"""
    json_files = list_files(PARAMS_FOLDER, extensions=[".json"])
    
    if not json_files:
        print("❌ Aucun test trouvé. Lancez `main.py` pour générer des données.")
        return

    config_scores = {}

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        best_config = data["best_config"]
        score = max(data["scores"].values(), default=0)
        mutated_score = mutate_score(score)

        if best_config in config_scores:
            config_scores[best_config].append(mutated_score)
        else:
            config_scores[best_config] = [mutated_score]

    avg_scores = {config: sum(scores) / len(scores) for config, scores in config_scores.items()}
    
    # Sélection des 5 meilleures configurations pour favoriser la diversité
    best_configs = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:5]

    print("\n📊 Analyse des paramètres OCR testés")
    for config, avg_score in best_configs:
        print(f"🔹 {config}: Score moyen {avg_score:.2f}")

    save_best_configurations({config: score for config, score in best_configs})
