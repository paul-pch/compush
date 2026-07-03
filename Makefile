.PHONY: install reinstall uninstall dev lint format clean

install:
	@echo "📦 Installation de compush avec uv..."
	uv tool install .
	@echo "✅ compush installé ! Utilisez: compush \"votre message\""

reinstall:
	@echo "🔄 Réinstallation de compush..."
	uv tool install --reinstall .
	@echo "✅ compush réinstallé !"

uninstall:
	@echo "🗑️ Désinstallation de compush..."
	uv tool uninstall compush
	@echo "✅ compush désinstallé"

dev:
	@echo "🔧 Installation en mode développement..."
	uv sync
	@echo "✅ Environnement de développement prêt !"
	@echo "💡 Utilisez: uv run compush \"votre message\""

lint:
	@echo "🔍 Vérification du code avec ruff..."
	uv run ruff check .

format:
	@echo "🎨 Formatage du code avec ruff..."
	uv run ruff check --fix .
	uv run ruff format .

clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	rm -rf .ruff_cache __pycache__ .venv uv.lock
	@echo "✅ Nettoyage terminé"
