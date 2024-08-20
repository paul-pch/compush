# Compush

`compush` est un petit utilitaire git pour me faire gagner du temps lors de mes développements.
Son objectif est d'embarquer tout le code non commité localement et de le push sur une branche remote.

## Get Starded

### Installer le binaire

```sh
    # Builder le binaire
    make

    # Recharger le terminal
    source ~/.zshrc
```

### Usage

```sh
    # Helper
    compush --help
```

## Fonctionnalités

* [x] Avoir un readme plus correct ..
* [x] Commit/Push tout le code en cours avec un message de commit passé en paramètre
* [x] Ne pas commit sur `master` ou `main`
* [x] Génération automatique d'un nom de branche spécifique par AI (mistral) si la branche courante est `master` ou `main`.
* [x] Créer automatiquement une MR gitlab avec un jeu de paramètres dédiés
* [ ] Générer le message de commit par IA en fonction du git diff
* [ ] Ajouter un mode offline
* [ ] Rendre la création de MR interractive pour simplifier la commande
* [ ] Ajouter une option pour push sur slack direct

