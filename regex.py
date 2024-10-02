import re

def get_ticket(string):
    # Expression régulière pour extraire la valeur entre parenthèses
    pattern = r'\(([A-Z]+-\d+)\)'

    # Recherche de la correspondance
    match = re.search(pattern, string)

    if match:
        return match.group(1)
    else:
        return None

def extract_after_first_colon(string: str) -> str:
    """
    Extrait tout ce qui se trouve après le premier ':' dans la chaîne de caractères.

    :param string: str, la chaîne de caractères à analyser.
    :return: str, la partie de la chaîne après le premier ':', ou une chaîne vide si ':' n'est pas trouvé.

    # Exemple d'utilisation
    string = "feat(TGDC-5572): Mise à jour du read(())'\"me un YTGDT-24 : test"
    result = extract_after_first_colon(string)
    print(result)  # Devrait afficher "Mise à jour du readme"
    """
    # Expression régulière pour extraire tout ce qui se trouve après le premier ':'
    pattern = r':\s*(.*)'

    # Recherche de la correspondance
    match = re.search(pattern, string)

    if match:
        return match.group(1)
    else:
        return ""
