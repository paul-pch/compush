# Compush

`compush` est un utilitaire git simple pour automatiser le workflow `git add` + `git commit` + `git push`.

## Caractéristiques

- 🚀 **Une seule commande** pour add/commit/push
- 🔀 **Gestion automatique des branches** : empêche les commits directs sur master/main
- 📝 **Prompt interactif** pour nommer une branche si vous êtes sur master
- ✨ **Simple et rapide** : pas de dépendances lourdes, juste Python et git

## Installation

### Prérequis

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installé (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git configuré

### Installation globale (recommandé)

```bash
# Dans le dossier du projet
make install
```

Vous pouvez maintenant utiliser `compush` depuis n'importe quel dossier !

### Mode développement

```bash
# Installer en mode dev
make dev

# Utiliser avec uv run
uv run compush "mon message de commit"
```

## Usage

### Commande de base

```bash
compush "mon message de commit"
```

Cette commande va :
1. Vérifier s'il y a des changements à commiter
2. Si vous êtes sur `master` ou `main`, vous demander un nom de branche
3. Exécuter `git add .`
4. Exécuter `git commit -m "mon message"`
5. Exécuter `git push` (avec `git push -u origin <branch>` si nécessaire)

### Options

```bash
# Forcer le commit sur master/main (à utiliser avec précaution)
compush "hotfix urgent" --master

# Spécifier un nom de branche (si sur master/main)
compush "nouvelle fonctionnalité" --branch feat/ma-feature

# Aide
compush --help
```

## Exemples

```bash
# Cas classique : vous êtes sur une branche feature
compush "fix: correction du bug #123"
# → git add . && git commit && git push

# Vous êtes sur master sans le savoir
compush "feat: nouvelle fonctionnalité"
# → Prompt: "Nom de la branche ?" → vous tapez "feat/ma-feature"
# → git checkout -b feat/ma-feature && git add . && git commit && git push

# Vous voulez vraiment commit sur master
compush "chore: update README" --master
# → git add . && git commit && git push (sur master)
```

## Développement

### Commandes utiles

```bash
# Linter
make lint

# Formatter
make format

# Réinstaller après modifications
make reinstall

# Nettoyer
make clean

# Désinstaller
make uninstall
```

### Pre-commit hooks

Le projet utilise pre-commit avec ruff pour le linting automatique :

```bash
# Installer les hooks
uv run pre-commit install

# Lancer manuellement
uv run pre-commit run --all-files
```

## Roadmap

- [x] Commit/Push automatique avec gestion de branches
- [x] Protection master/main
- [x] Prompt interactif pour nommer les branches
- [ ] Génération automatique du nom de branche (LLM, conventional commits, etc.)
- [ ] Génération automatique du message de commit basé sur le diff
- [ ] Configuration personnalisable (branches protégées, remote par défaut, etc.)

## License

MIT
