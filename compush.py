"""Compush CLI"""
#!/usr/bin/python3

import json
import os
import subprocess
import sys
from typing import List, Optional

import httpx
import typer
from mistralai import Mistral
from rich import print
from rich.prompt import Prompt
from typing_extensions import Annotated

import gitlab_utils
import regex
import renderer


def main(
    commit_message: Annotated[str, typer.Argument(help="Message de commit à pusher avec les modifications en cours.")],
    master: Annotated[Optional[bool], typer.Option(help="Permet de forcer le push sur master")] = False,
    branch: Annotated[
        Optional[str], typer.Option(help="Permet de forcer un nom de branche git (seulement si l'actuelle est master ou main)")
    ] = None,
    remote: Annotated[Optional[str], typer.Option(help="Permet de préciser un remote git déjà configuré")] = "origin",
    mr: Annotated[Optional[bool], typer.Option(help="Déclenche la création d'une merge request sur gitlab")] = False,
    label: Annotated[Optional[str], typer.Option(help="Mode MR - Permet d'ajouter un label à la merge request")] = None,
    time_review: Annotated[
        Optional[str], typer.Option(help="Mode MR - Permet d'ajouter un temps de relecture à la merge request")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option(help="Mode MR - Permet d'ajouter un entête descriptif à la merge request")
    ] = None,
    task: Annotated[
        Optional[List[str]],
        typer.Option(help="Mode MR - Permet d'ajouter des tâches réalisées à la description de merge request"),
    ] = None,
    env: Annotated[
        Optional[List[str]], typer.Option(help="Mode MR - Permet d'ajouter des environnements à la description de merge request")
    ] = None,
    test: Annotated[
        Optional[List[str]], typer.Option(help="Mode MR - Permet d'ajouter des tests à la description de merge request")
    ] = None,
    notes: Annotated[Optional[str], typer.Option(help="Mode MR - Permet d'ajouter des notes à la merge request")] = None,
):
    """Fonction racine"""

    # Commit code
    commit_code(commit_message, master, branch, remote)

    # Merge Request
    if mr:
        create_merge_request(commit_message, description, time_review, label, task, env, test, notes)


def commit_code(commit_message: str, master: bool, branch: str, remote: str):
    """Méthode de commit et push du code courant"""

    # Vérifie si des changements sont en attente
    result = subprocess.run(["git status --porcelain=v1 | wc -l"], shell=True, capture_output=True, check=False)
    changements_git = int(result.stdout.decode().strip())
    if changements_git == 0:
        print("[bold green]:white_check_mark: Pas de changement détecté ![/bold green]")
    else:
        # Vérifie que la branche n'est pas 'master' ou 'main'
        # Génère une branche en fonction du commit message et se positionne dessus
        print("[bold]:left_arrow_curving_right: Vérification de la branche ..[/bold]")
        current_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
        if current_branch in ["master", "main"] and not master:
            new_branch = branch
            if not branch:
                print("[bold yellow]:warning: Master detected ![/bold yellow]")
                new_branch = generate_branch_name_ai(commit_message)

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


def create_merge_request(
    commit_message: str,
    description: str,
    time_review: str,
    label: str,
    tasks: List[str],
    envs: List[str],
    tests: List[str],
    notes: str,
):
    """Méthode de création de merge request avec les informations passées en paramètre"""

    print("\n[bold]:left_arrow_curving_right: Création merge request ..[/bold]")

    if subprocess.getoutput("git rev-parse --abbrev-ref HEAD") in ["master", "main"]:
        print(
            "\n[bold yellow]:warning: :safety_vest: Attention ! La branche courante est déjà master ou main. Pas de MR possible.[/bold yellow]"
        )
        sys.exit(0)

    # Vérification des variables obligatoires

    # Time_review
    if not time_review:
        print(
            '\n[bold yellow]:warning: Attention ! En mode MR, veuillez renseigner un temps de relecture : --time-review "2 mins" [/bold yellow]'
        )
        sys.exit(1)

    # Personnal Access Token
    try:
        token = os.environ["SIV_GITLAB_PRIVATE_TOKEN"]
    except KeyError:
        print(
            '\n[bold yellow]:warning: Attention ! En mode MR, veuillez charger dans votre contexte la variable: "SIV_GITLAB_PRIVATE_TOKEN" [/bold yellow]'
        )
        sys.exit(1)

    # Construction des variables générales
    project_id = gitlab_utils.get_project_id(token, get_current_directory_name(), "siv")
    url = f"https://innersource.soprasteria.com/api/v4/projects/{project_id}/merge_requests"
    title = commit_message
    params = f"title={title}"
    if not description:
        description = regex.extract_after_first_colon(commit_message)
    jeux_de_variables = {
        "description": description,
        "time_review": time_review,
    }

    # Ticket
    ticket = regex.get_ticket(commit_message)
    if ticket:
        jeux_de_variables["ticket"] = ticket

    # Tâches
    if tasks:
        jeux_de_variables["tasks"] = tasks

    # Envs
    if envs:
        jeux_de_variables["envs"] = envs

    # Tests
    if tests:
        jeux_de_variables["tests"] = tests

    # Notes
    if notes:
        jeux_de_variables["notes"] = notes

    # Description
    mr_description = renderer.build_mr_description(jeux_de_variables)
    if mr_description:
        # print(mr_description)
        params += f"&description={mr_description}"

    # Labels
    if label:
        params += f"&labels={label}"

    # Branches
    source_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
    try:
        target_branch = get_default_branch()
    except Exception as e:
        print(e)
        sys.exit(1)
    params += f"&source_branch={source_branch}&target_branch={target_branch}"

    command = ["curl", "--request", "POST", "--header", f"PRIVATE-TOKEN: {token}", "--data", f"{params}", url]

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        print("\n[bold green]:white_check_mark: Merge request créée avec succès. ![/bold green]")
        projects = json.loads(result.stdout)
        print(f"\n[bold]:left_arrow_curving_right: {projects.get('web_url')} [/bold]")

    else:
        print("\n[bold red]:building_construction: Erreur - Problème lors du push du code ... [/bold red]")
        print("Erreur: ", result.stderr)
        sys.exit(1)


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
            ["git", "show-ref", "--verify", f"refs/heads/{branch}"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return branch
    raise Exception("\n[bold yellow]:warning: Attention ! Aucune des branches 'master' ou 'main' n'existe. [/bold yellow]")


def generate_branch_name_ai(commit: str):
    """Génère un nom de branche au travers de l'API Mistral AI"""

    try:
        api_key = os.environ["MISTRAL_API_KEY"]
    except Exception:
        print("\n[bold red]:warning:  Erreur - variable MISTRAL_API_KEY manquante ... [/bold red]")
        sys.exit(1)

    MODEL = "mistral-large-latest"
    client = Mistral(api_key=api_key, client=httpx.Client(verify=False))

    print("\n[bold]:left_arrow_curving_right: Génération d'une branche.. [/bold]")
    directives = [
        f"Génère moi un nom de branch en fonction du nom de commit suivant : {commit} .",
        "Je veux que la branche respecte les normes de conventionnal commit",
        "exemple: feat/ajout_fonctionnalite_simpleRenvoie moi uniquement le nom de la branche et rien d'autre.",
        "Reformule légèrement pour une simplicité maximale, enlève les doublons et les connecteurs.",
        "Pas d'accent ou caractères spéciaux. Pas de quote, rien que la branche en pure string.",
    ]

    requete = " ".join(directives)

    try:
        chat_response = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": requete,
                },
            ],
        )
    except Exception as e:
        print(e)
        print("[bold yellow]:warning: Echec de l'appel à Mistral.[/bold yellow]\n")
        branch_name = Prompt.ask("[bold blue]:right_arrow:  Entrez un nom de branche [/bold blue]")
        return branch_name

    return chat_response.choices[0].message.content.strip()


if __name__ == "__main__":
    typer.run(main)
