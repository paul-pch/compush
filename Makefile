PYTHON := python3
VENV_DIR := venv

all: install integrate

.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV_DIR)

.PHONY: upgrade
upgrade:
	./scripts/upgrade.sh requirements.txt

install:
	pyinstaller --onefile compush.py

integrate:
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
