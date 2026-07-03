"""Compush CLI"""
# !/usr/bin/python3

import os
import subprocess
import sys
from typing import List, Optional

import typer
from rich import print
from typing_extensions import Annotated


def main(
    commit_message: Annotated[
        str,
        typer.Argument(help="Message de commit à pusher avec les modifications en cours."),
    ],
    master: Annotated[Optional[bool], typer.Option(help="Permet de forcer le push sur master")] = False,
    branch: Annotated[
        Optional[str],
        typer.Option(help="Permet de forcer un nom de branche git (seulement si l'actuelle est master ou main)"),
    ] = None,
    remote: Annotated[
        Optional[str],
        typer.Option(help="Permet de préciser un remote git déjà configuré"),
    ] = "origin",
    label: Annotated[
        Optional[str],
        typer.Option(help="Mode MR - Permet d'ajouter un label à la merge request"),
    ] = None,
    time_review: Annotated[
        Optional[str],
        typer.Option(help="Mode MR - Permet d'ajouter un temps de relecture à la merge request"),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option(help="Mode MR - Permet d'ajouter un entête descriptif à la merge request"),
    ] = None,
    task: Annotated[
        Optional[List[str]],
        typer.Option(help="Mode MR - Permet d'ajouter des tâches réalisées à la description de merge request"),
    ] = None,
    env: Annotated[
        Optional[List[str]],
        typer.Option(help="Mode MR - Permet d'ajouter des environnements à la description de merge request"),
    ] = None,
    test: Annotated[
        Optional[List[str]],
        typer.Option(help="Mode MR - Permet d'ajouter des tests à la description de merge request"),
    ] = None,
    notes: Annotated[
        Optional[str],
        typer.Option(help="Mode MR - Permet d'ajouter des notes à la merge request"),
    ] = None,
):
    """Fonction racine"""

    # Commit code
    commit_code(commit_message, master, branch, remote)


def commit_code(commit_message: str, master: bool, branch: str, remote: str):
    """Méthode de commit et push du code courant"""

    # Vérifie si des changements sont en attente
    result = subprocess.run(
        ["git status --porcelain=v1 | wc -l"],
        shell=True,
        capture_output=True,
        check=False,
    )
    changements_git = int(result.stdout.decode().strip())
    if changements_git == 0:
        print("[bold green]:white_check_mark: Pas de changement détecté ![/bold green]")
    else:
        # Vérifie que la branche n'est pas 'master' ou 'main'
        # Génère une branche en fonction du commit message et se positionne dessus
        print("[bold]:left_arrow_curving_right: Vérification de la branche ..[/bold]")
        current_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
        if current_branch in ["master", "main"] and not master:
            new_branch: str = branch
            if not branch:
                print("[bold yellow]:warning: Master detected ![/bold yellow]")
                new_branch = input("Saisissez le nom de la branche : ")

            print(f"\n[bold]:left_arrow_curving_right: Changement de branche: {new_branch} [/bold]")
            subprocess.run([f"git checkout -b {new_branch}"], shell=True, check=True)
        elif branch and branch != current_branch:
            subprocess.run([f"git checkout -b {branch}"], shell=True, check=True)

        # Commit du code
        print("\n[bold]:left_arrow_curving_right: Commit/push ..[/bold]")
        subprocess.run(["git add ."], shell=True, check=True)
        subprocess.run([f'git commit -m "{commit_message}"'], shell=True, check=True)

        result = subprocess.run(["git", "remote"], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            push = subprocess.run(["git push"], shell=True, check=True)
            if push.returncode == 0:
                print("\n[bold green]:white_check_mark: Code compushed ![/bold green]")
            else:
                print("\n[bold red]:building_construction: Erreur - Problème lors du push du code ... [/bold red]")
                sys.exit(1)
        else:
            print("\n[bold yellow]:warning: :safety_vest: Aucun remote n'est configuré.[/bold yellow]")


def get_current_directory_name():
    """Renvoie le nom du dossier courant"""
    # Obtenir le chemin du répertoire courant
    current_path = os.getcwd()
    # Extraire le nom du dossier à partir du chemin
    current_directory_name = os.path.basename(current_path)
    return current_directory_name


def get_default_branch():
    """Renvoie le nom de la branche courante"""
    branches = ["master", "main"]
    for branch in branches:
        result = subprocess.run(
            ["git", "show-ref", "--verify", f"refs/heads/{branch}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return branch
    raise Exception(
        "\n[bold yellow]:warning: Attention ! Aucune des branches 'master' ou 'main' n'existe. [/bold yellow]"
    )


def generate_branch_name_ai(commit: str):
    """Génère un nom de branche au travers de l'API Mistral AI"""

    # directives = [
    #     f"Génère moi un nom de branch en fonction du nom de commit suivant : {commit} .",
    #     "Je veux que la branche respecte les normes de conventionnal commit",
    #     "exemple: feat/ajout_fonctionnalite_simpleRenvoie moi uniquement le nom de la branche et rien d'autre.",
    #     "Reformule légèrement pour une simplicité maximale, enlève les doublons et les connecteurs.",
    #     "Pas d'accent ou caractères spéciaux. Pas de quote, rien que la branche en pure string.",
    # ]

    print("[bold yellow]:warning: Echec de l'appel à Mistral.[/bold yellow]\n")
    branch_name = Prompt.ask("[bold blue]:right_arrow:  Entrez un nom de branche [/bold blue]")
    return branch_name


if __name__ == "__main__":
    typer.run(main)
