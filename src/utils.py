import os

def list_files(directory, extensions=None):
    """Récupère la liste des fichiers d'un dossier selon les extensions spécifiées"""
    files = []
    for file in os.listdir(directory):
        if extensions:
            if any(file.lower().endswith(ext) for ext in extensions):
                files.append(os.path.join(directory, file))
        else:
            files.append(os.path.join(directory, file))
    return files
