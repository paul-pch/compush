"""Compush CLI"""
#!/usr/bin/python3

from typing import Optional

import os
import subprocess
import sys
import typer
import json

from mistralai import Mistral
from rich import print
from typing_extensions import Annotated

import gitlab_utils

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
client = Mistral(api_key=api_key)


def main(
    commit_message: Annotated[str, typer.Argument(help="Message de commit à pusher avec les modifications en cours.")],
    master: Annotated[Optional[bool], typer.Option(help="Permet de forcer le push sur master")] = False,
    branch: Annotated[Optional[str], typer.Option(help="Permet de forcer un nom de branche git (seulement si l'actuelle est master ou main)")] = None,
    mr: Annotated[Optional[bool], typer.Option(help="Déclenche la création d'une merge request sur gitlab")] = False,
    label: Annotated[Optional[str], typer.Option(help="Mode MR - Permet d'ajouter un label à la merge request")] = None,
    description: Annotated[Optional[str], typer.Option(help="Mode MR - Permet d'ajouter une description à la merge request")] = None
):
    """Fonction racine"""

    ## Commit code
    commit_code(commit_message, master, branch)

    ## Merge Request
    if mr:
        create_merge_request(commit_message, description, label)

def commit_code(commit_message: str, master: bool, branch: str):
    """Méthode de commit et push du code courant"""

    # Vérifie si des changements sont en attente
    result = subprocess.run(["git status --porcelain=v1 | wc -l" ], shell=True, capture_output=True, check=False)
    changements_git = int(result.stdout.decode().strip())
    if changements_git == 0:
        print("[bold green]:white_check_mark: Pas de changement détecté ![/bold green]")
    else:
        # Vérifie que la branche n'est pas 'master' ou 'main'
        ## Génère une branche en fonction du commit message et se positionne dessus
        print("[bold]:left_arrow_curving_right: Vérification de la branche ..[/bold]")
        current_branch = subprocess.getoutput('git rev-parse --abbrev-ref HEAD')
        if current_branch in ["master", "main"] and not master:
            new_branch = branch
            if not branch:
                print("[bold yellow]:warning: Master detected ![/bold yellow]")
                new_branch = generate_branch_name_ai(commit_message)

            print(f"\n[bold]:left_arrow_curving_right: Changement de branche: {new_branch} [/bold]")
            subprocess.run([f"git checkout -b {new_branch}"], shell=True, check=False)
            subprocess.run([f"git push -u origin {new_branch}"], shell=True, check=False)


        # Commit du code
        print("\n[bold]:left_arrow_curving_right: Commit/push ..[/bold]")
        subprocess.run(['git add .'], shell=True, check=False)
        subprocess.run([f"git commit -m \"{commit_message}\""], shell=True, check=False)

        push = subprocess.run(['git push'], shell=True, check=True)
        if push.returncode == 0:
            print("\n[bold green]:white_check_mark: Code compushed ![/bold green]")
        else:
            print("\n[bold red]:building_construction: Erreur - Problème lors du push du code ... [/bold red]")
            sys.exit(1)

def create_merge_request(commit_message: str, description: str, label: str):
    """Méthode de création de merge request avec les informations passées en paramètre"""

    print("\n[bold]:left_arrow_curving_right: Création merge request ..[/bold]")

    # Vérification des variables obligatoires

    ## Description
    if not description:
        print("\n[bold yellow]:warning: Attention ! En mode MR, veuillez renseigner une description : --description \"une description\" [/bold yellow]")
        sys.exit(1)

    ## Personnal Access Token
    try:
        token = os.environ["ERPC_GITLAB_PRIVATE_TOKEN"]
    except KeyError:
        print("\n[bold yellow]:warning: Attention ! En mode MR, veuillez charger dans votre contexte la variable : \"ERPC_GITLAB_PRIVATE_TOKEN\" [/bold yellow]")
        sys.exit(1)


    # Construction des variables générales
    project_id = gitlab_utils.get_project_id(token, get_current_directory_name(), "erpc-group")
    url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests"

    # Titre
    title = commit_message
    params = f"title={title}"

    # Description
    # description = "test"
    params += f"&description={description}"

    # Labels
    if label:
        params += f"&labels={label}"


    ## Branches
    source_branch = subprocess.getoutput('git rev-parse --abbrev-ref HEAD')
    try:
        target_branch = get_default_branch()
    except Exception as e:
        print(e)
        sys.exit(1)
    params += f"&source_branch={source_branch}&target_branch={target_branch}"


    command = [
        "curl",
        "--request", "POST",
        "--header", f"PRIVATE-TOKEN: {token}",
        "--data", f"{params}",
        url
    ]

    print(command)

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        print("\n[bold green]:white_check_mark: Merge request créée avec succès. ![/bold green]")
        projects = json.loads(result.stdout)
        print(f"\n[bold]:left_arrow_curving_right: {projects.get("web_url")} [/bold]")

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
        result = subprocess.run(['git', 'show-ref', '--verify', f'refs/heads/{branch}'], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            return branch
    raise Exception("\n[bold yellow]:warning: Attention ! Aucune des branches 'master' ou 'main' n'existe. [/bold yellow]")

def generate_branch_name_ai(commit: str):
    """Génère un nom de branche au travers de l'API Mistral AI"""

    print("\n[bold]:left_arrow_curving_right: Génération d'une branche.. [/bold]")
    directives = [
        f"Génère moi un nom de branch en fonction du nom de commit suivant : {commit} .",
        "Je ne veux pas de / ou de - mais des _ à la place.",
        "Renvoie moi uniquement le nom de la branche et rien d'autre.",
        "Reformule légèrement, enlève les doublons et les connecteurs"
        ]

    requete = ' '.join(directives)

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": requete,
            },
        ]
    )

    return chat_response.choices[0].message.content

if __name__ == "__main__":
    typer.run(main)
