#!/usr/bin/env python3
"""Compush - Git add, commit et push automatisé avec gestion de branches"""

import subprocess
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

app = typer.Typer()
console = Console()


def run_git_command(command: list[str]) -> tuple[bool, str]:
    """Exécute une commande git et retourne (succès, output)"""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def get_current_branch() -> str:
    """Retourne la branche courante"""
    success, output = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return output if success else ""


def generate_branch_name_ai(commit_message: str) -> str:
    """
    Génère un nom de branche.

    TODO: Ajouter une logique automatisée (LLM, parsing du message, conventional commits, etc.)
    Pour l'instant, prompt interactif simple.

    Args:
        commit_message: Message de commit pour inspirer le nom de branche

    Returns:
        Le nom de la branche choisi par l'utilisateur
    """
    console.print(f"[cyan]Message de commit: {commit_message}[/cyan]")
    branch_name = Prompt.ask("[bold yellow]Nom de la branche[/bold yellow]")
    return branch_name


@app.command()
def main(
    commit_message: str = typer.Argument(..., help="Message de commit à pusher avec les modifications en cours"),
    master: bool = typer.Option(False, "--master", help="Permet de forcer le push sur master/main"),
    branch: Optional[str] = typer.Option(
        None, "--branch", help="Permet de forcer un nom de branche (seulement si l'actuelle est master ou main)"
    ),
):
    """Git add, commit et push en une commande avec gestion automatique des branches"""

    # Vérifier s'il y a des changements
    success, output = run_git_command(["git", "status", "--porcelain"])
    if not success:
        console.print("[bold red]Erreur lors de la vérification du statut git[/bold red]")
        sys.exit(1)

    if not output.strip():
        console.print("[bold green]✅ Pas de changement détecté ![/bold green]")
        return

    # Vérifier la branche courante
    console.print("[bold]🔍 Vérification de la branche...[/bold]")
    current_branch = get_current_branch()

    if not current_branch:
        console.print("[bold red]Erreur: Impossible de déterminer la branche courante[/bold red]")
        sys.exit(1)

    console.print(f"[cyan]Branche courante: {current_branch}[/cyan]")

    # Gestion des branches master/main
    if current_branch in ["master", "main"] and not master:
        new_branch = branch
        if not branch:
            console.print("[bold yellow]⚠️ Master détecté ![/bold yellow]")
            new_branch = generate_branch_name_ai(commit_message)

        console.print(f"\n[bold]🔀 Changement de branche: {new_branch}[/bold]")
        success, error = run_git_command(["git", "checkout", "-b", new_branch])
        if not success:
            console.print(f"[bold red]Erreur lors de la création de la branche: {error}[/bold red]")
            sys.exit(1)

    elif branch and branch != current_branch:
        console.print(f"\n[bold]🔀 Changement de branche: {branch}[/bold]")
        success, error = run_git_command(["git", "checkout", "-b", branch])
        if not success:
            console.print(f"[bold red]Erreur lors de la création de la branche: {error}[/bold red]")
            sys.exit(1)

    # Git add
    console.print("[bold]📦 Git add...[/bold]")
    success, error = run_git_command(["git", "add", "."])
    if not success:
        console.print(f"[bold red]Erreur git add: {error}[/bold red]")
        sys.exit(1)

    # Git commit
    console.print(f"[bold]💬 Git commit: {commit_message}[/bold]")
    success, error = run_git_command(["git", "commit", "-m", commit_message])
    if not success:
        console.print(f"[bold red]Erreur git commit: {error}[/bold red]")
        sys.exit(1)

    # Vérifier si un remote existe
    success, remotes = run_git_command(["git", "remote"])
    if not success or not remotes.strip():
        console.print("\n[bold yellow]⚠️ Aucun remote n'est configuré[/bold yellow]")
        console.print("[bold green]✅ Code commité localement (pas de push)[/bold green]")
        return

    # Git push
    console.print("[bold]🚀 Git push...[/bold]")
    success, error = run_git_command(["git", "push"])

    if not success:
        # Tentative avec -u origin si la branche n'est pas trackée
        console.print("[yellow]⚠️ Push échoué (branche non trackée)[/yellow]")
        console.print("[yellow]💡 Essai avec -u origin...[/yellow]")
        current_branch = get_current_branch()
        success, error = run_git_command(["git", "push", "-u", "origin", current_branch])

        if not success:
            console.print(f"[bold red]🚨 Erreur - Problème lors du push du code: {error}[/bold red]")
            sys.exit(1)

    console.print("\n[bold green]✅ Code compushed ![/bold green]")


if __name__ == "__main__":
    app()
