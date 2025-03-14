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

### Exemple

```sh
    # Commit et push le code et créer une MR avec les paramètre renseignés
    compush "feat(TGDC-5572): Ajout nouvelle fonctionnalité des plus intéressantes" \
        --mr \
        --label ops \
        --time-review "2 heures" \
        --task "OKAjout d'une nouvelle fonction" \
        --task "BSR: Nettoyage code sale" \
        --env dev \
        --env OKprod \
        --test "OKLe bug est réparé" \
        --notes "Voilà une super note !"
```

## Fonctionnalités

- [x] Avoir un readme plus correct ..
- [x] Commit/Push tout le code en cours avec un message de commit passé en paramètre
- [x] Ne pas commit sur `master` ou `main`
- [x] Génération automatique d'un nom de branche spécifique par AI (mistral) si la branche courante est `master` ou `main`.
- [x] Créer automatiquement une MR gitlab avec un jeu de paramètres dédiés
- [x] Ajouter un mode offline
- [ ] Utiliser des noms de branche avec des '/' exemple -> fix/un_correctif_parmis_dautres
- [ ] Ajouter une option pour push sur Teams direct

- [ ] Ajouter `git config --global push.default current` si un git push fail à cause de : fatal: The current branch chore_test has no upstream branch
- [ ] Générer le message de commit par IA en fonction du git diff
- [ ] Rendre la création de MR interractive pour simplifier la commande

