#!/usr/bin/python3

import os
import subprocess
import typer

from mistralai import Mistral
from rich import print
from typing import List, Optional
from typing_extensions import Annotated

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
client = Mistral(api_key=api_key)



def main(
    commit_message: Annotated[str, typer.Argument(help="Message à intégrer au commit")],
    master: Annotated[Optional[bool], typer.Option(help="Permet de forcer le push sur master")] = False,
    mr: Annotated[Optional[List[str]], typer.Option(help="Déclenche la création d'une merge request sur gitlab")] = None
):

    # Vérifie si des changements sont en attente
    result = subprocess.run(["git status --porcelain=v1 | wc -l" ], shell=True, capture_output=True)
    changements_git = int(result.stdout.decode().strip())
    if changements_git == 0:
        print("[bold green]:white_check_mark: Pas de changement détectés ![/bold green]")
        quit()


    # Vérifie que la branche n'est pas 'master' ou 'main'
    ## Génère une branche en fonction du commit message et se positionne dessus
    print("[bold]:left_arrow_curving_right: Vérification de la branche ..[/bold]")
    current_branch = subprocess.getoutput('git rev-parse --abbrev-ref HEAD')
    print(current_branch)
    if current_branch in ["master", "main"] and not master:
        print("[bold yellow]:warning: Master detected ![/bold yellow]")
        new_branch = generateBranchNameAI(commit_message)
        print(f"[bold]:left_arrow_curving_right: Changement de branche: {new_branch} [/bold]")
        subprocess.run([f"git checkout -b {new_branch}"], shell=True)
        subprocess.run([f"git push -u origin {new_branch}"], shell=True)


    # Commit du code
    print("[bold]:left_arrow_curving_right: Commit/push ..[/bold]")
    subprocess.run(['git add .'], shell=True)
    subprocess.run([f"git commit -m \"{commit_message}\""], shell=True)
    subprocess.run(['git push'], shell=True)

    print("[bold green]:white_check_mark: Code compushed ![/bold green]")




    # Merge Request Section
    # if mr:
    #     print(f"No provided users (raw input = {user})")
    #     raise typer.Abort()
    # for u in user:
    #     print(f"Processing user: {u}")

    # --title
    # --description (default value)
    # --label (optional)
    # --task (optional)
    # --test (optional)
    # --env (optional)
    # --notes


def generateBranchNameAI(commit: str):
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

# TODO
# def generateCommitMessage(gitDiff: str):

if __name__ == "__main__":
    typer.run(main)
