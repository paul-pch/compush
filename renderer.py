import sys

from typing import Dict

import template.mr_erpc

def build_mr_description(jeux_de_variables: Dict[str, str]):
    required_keys = {'description', 'time_review'}
    for key in required_keys:
        if key not in jeux_de_variables:
            raise KeyError(f"La clé '{key}' est manquante dans les variables fournies.")
        if not isinstance(jeux_de_variables[key], str):
            raise TypeError(f"La valeur de la clé '{key}' doit être une chaîne de caractères.")


    mr_description = render_template(template.mr_erpc.erpc_init, jeux_de_variables)

    if 'ticket' in jeux_de_variables and jeux_de_variables['ticket']:
        mr_description += render_template(template.mr_erpc.erpc_ticket, jeux_de_variables)

    if 'tasks' in jeux_de_variables and jeux_de_variables['tasks']:
        mr_description += template.mr_erpc.erpc_tasks_title
        for task in jeux_de_variables['tasks']:
            mr_description += format_checkbox(task)

    if 'envs' in jeux_de_variables and jeux_de_variables['envs']:
        mr_description += template.mr_erpc.erpc_env_title
        for env in jeux_de_variables['envs']:
            mr_description += format_checkbox(env)

    if 'tests' in jeux_de_variables and jeux_de_variables['tests']:
        mr_description += template.mr_erpc.erpc_tests_title
        for test in jeux_de_variables['tests']:
            mr_description += format_checkbox(test)

    if 'notes' in jeux_de_variables and jeux_de_variables['notes']:
        mr_description += render_template(template.mr_erpc.erpc_notes, jeux_de_variables)

    return mr_description



def render_template(template, variables):
    """
    Remplace les placeholders dans le template par les valeurs des variables.

    :param template: str, le contenu du template Markdown avec des placeholders.
    :param variables: dict, un dictionnaire contenant les variables à remplacer.
    :return: str, le template enrichi avec les variables.
    """
    try:
        return template.format(**variables)
    except KeyError as e:
        print(f"Erreur: Le placeholder '{e.args[0]}' n'a pas été trouvé dans les variables fournies.")
        sys.exit(1)

def format_checkbox(task: str) -> str:
    """
    Formate une chaîne de caractères en fonction de son préfixe.

    :param task: str, la chaîne de caractères à formater.
    :return: str, la chaîne de caractères formatée.

    # Exemple d'utilisation
    task1 = "OKAjout d'une task de création de droit"
    task2 = "Ajout d'une task de création de droit"

    formatted_task1 = format_task(task1)
    formatted_task2 = format_task(task2)

    print(formatted_task1)  # Devrait afficher "* [x] Ajout d'une task de création de droit"
    print(formatted_task2)  # Devrait afficher "* [ ] Ajout d'une task de création de droit"
    """
    if task.startswith("OK"):
        formatted_task = "* [x] " + task[2:].strip() + "\n"
    else:
        formatted_task = "* [ ] " + task.strip() + "\n"

    return formatted_task



#### ==========
# Exemple d'utilisation

# template = """
# Temps de review : **~{time_review}>.**

# ## Pourquoi cette MR ?

# {description}

# """

# variables = {
#     "objectif": "améliorer la documentation",
#     "date_debut": "01/01/2023",
#     "responsable": "Jean Dupont",
#     "statut": "En cours"
# }

# rendered_template = render_template(template, variables)

# if rendered_template:
#     print(rendered_template)



#### ==========
# A ajouter

# ## Ce qui a été fait dans cette MR

# <Expliquer ce qui a été fait pour résoudre notre problématique>

# * [ ] <FOREACH --task>

# <Identifier les environnements concernés (liste non exhaustive car dépendante des projets)>
# * [ ] <FOREACH --env>


# ## Tests d'acceptance

# <Expliquer la marche à suivre pour valider que le comportement recherché est bien implémenté>
# * [ ] <FOREACH --test>


# ## Note(s)

# notes <NOTES --notes>
