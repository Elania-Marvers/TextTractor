import difflib
import re
from collections import Counter
from text_unidecode import unidecode
import json
import os
from utils import list_files

TRAINING_FOLDER = "training_test"

COMMON_WORDS = {"bonjour", "merci", "document", "texte", "informations", "analyse", "extraction", "test", "ocr", "image", "lecture", "phrase", "probable", "résultat", "fichier"}

# Chargement des textes de référence pour comparaison
expected_texts = {
    "ecriture_manuscrite_0": """Je soussigné Dr Bertrand Coulon, certifie avoir examiné le 4/11/2024 à 21h M. Renneson Baptiste né le 10/9/2002, domicilié 21A rue de Bourgogne 21420 Savigny-les-Beaune.
J'ai constaté ce qui suit :
- anxiété généralisée
- somatisation du stress
- stress post-traumatique
Il en résulte une ITT de 7 jours.""",
    
    "scan_lettre_0": """Monsieur Baptiste RENNESON-BOUTARD
21A rue de Bourgogne
21420 SAVIGNY LES BEAUNE

Objet : absence injustifiée

Monsieur,

Vous êtes absent de votre lieu de travail depuis le mardi 22 octobre 2024.
Le même jour à 11h00 nous vous avons envoyé un courriel constatant votre absence.
Le lendemain, mercredi 30 octobre 2024, nous avons reçu un courriel qui nous informait qu’un médecin vous avait prescrit un arrêt maladie jusqu’au 3 novembre 2024.
Vous nous avez écrit en outre avoir posté ledit arrêt à destination de l’entreprise.
À ce jour nous n’avons toujours pas reçu votre arrêt maladie.
Nous vous mettons en demeure de nous produire ledit document.
À défaut vous vous exposez à des sanctions disciplinaires pouvant aller jusqu’au licenciement pour faute.""",
    
    "screen_disc_0": """Elie San 14/08/2024 19:13
Je rappelle les noms de groupes sont random

Kwame42 22/08/2024 17:00
C'est top ! Je vois des mails tomber de tests dans tous les sens 😆""",
    
    "screen_disc_1": """Kwame42 Je ne sais pas ce que tu considères dans "ce qu'il a fait" je pourrais te répondre également : "il t...

Elie San 30/08/2024 09:35
Et bah là est tout le problème vous êtes persuadé qu’il a tenté de me sauver la vie et pensez que je suis déséquilibré voilà le vrai problème.

Kwame42 30/08/2024 17:11
Non Elie. Ce n’est pas ce que je t’ai écrit. Ce n’est pas parce que je te dis que Abdel t’a sauvé (avec un témoin autour) que je pense que tu es un déséquilibré.
L’un et l’autre ne sont pas liés.
C’est aussi simple que ça.
Abdel c’est abdel, toi c’est toi.
Abdel, et j’étais et tu me l’as dit, t’as détaché."""
}

def compute_similarity(text1, text2):
    """Calcule la similarité entre deux textes."""
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def evaluate_ocr_result(file_name, extracted_text):
    """Évalue la qualité de l'OCR en comparant le texte extrait au texte attendu."""
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    if base_name in expected_texts:
        reference_text = expected_texts[base_name]
        score = compute_similarity(reference_text, extracted_text)
        return score
    return None  # Aucun texte de référence disponible



def clean_text(text):
    """Nettoie le texte OCR (espaces, accents, caractères spéciaux)"""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = unidecode(text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def refine_ocr_results(texts):
    """Analyse les résultats OCR et retourne la meilleure prédiction"""
    cleaned_texts = [clean_text(txt) for txt in texts]
    counter = Counter(cleaned_texts)
    most_common_text, _ = counter.most_common(1)[0]

    # 🔍 Comparaison avec les anciens résultats
    past_results = list_files(TRAINING_FOLDER, extensions=[".json"])
    
    for past_file in past_results:
        with open(past_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        old_text = clean_text(data["optimized_text"])
        
        if difflib.SequenceMatcher(None, most_common_text, old_text).ratio() > 0.85:
            print(f"⚠️ Amélioration détectée : Ancien texte plus fiable trouvé")
            return data["optimized_text"]  # Utilisation de l'ancien meilleur résultat

    return most_common_text
