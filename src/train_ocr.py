import os
import json
from utils import list_files

PARAMS_FOLDER = "training_params"

def analyze_best_configs():
    """Analyse les tests précédents pour identifier la meilleure configuration OCR en pondérant les scores"""
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
        
        if best_config in config_scores:
            config_scores[best_config].append(score)
        else:
            config_scores[best_config] = [score]

    # 🎯 Calcul des scores moyens
    avg_scores = {config: sum(scores) / len(scores) for config, scores in config_scores.items()}
    
    # 🏆 Sélection des 3 meilleures configurations
    best_configs = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    print("\n📊 Analyse des paramètres OCR testés")
    for config, avg_score in best_configs:
        print(f"🔹 {config}: Score moyen {avg_score:.2f}")

    # 🎯 Sélection finale
    best_global_config = best_configs[0][0]

    print(f"\n✅ Meilleure configuration actuelle : {best_global_config}")

    # Enregistrement du meilleur paramètre
    best_config_file = os.path.join(PARAMS_FOLDER, "best_config.json")
    with open(best_config_file, "w", encoding="utf-8") as f:
        json.dump({"best_config": best_global_config}, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    analyze_best_configs()
