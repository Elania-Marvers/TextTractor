# Variables
PYTHON = python3
VENV = .venv
SRC = src
TESTPOOL = testpool

# Installation des dépendances
install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	sudo apt update && sudo apt install tesseract-ocr -y
	sudo apt install tesseract-ocr-fra -y


# Activation de l’environnement virtuel
activate:
	@echo "Run: source $(VENV)/bin/activate"

# Lancement de TexTractor
run:
	$(VENV)/bin/python $(SRC)/main.py --folder $(TESTPOOL)

# Test sur les fichiers du testpool
test:
	$(VENV)/bin/python $(SRC)/main.py --folder $(TESTPOOL)

# Nettoyage des fichiers temporaires
clean:
	rm -rf $(VENV) __pycache__ *.log

.PHONY: install activate run test clean
