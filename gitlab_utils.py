import subprocess
import json

def get_project_id(api_token, project_name, keyword):
    """Commande curl pour rechercher un projet"""
    
    curl_command = [
        "curl", "-s",
        "-H", f"PRIVATE-TOKEN: {api_token}",
        f"https://gitlab.com/api/v4/projects?search={project_name}"
    ]

    # Exécuter la commande curl
    result = subprocess.run(curl_command, capture_output=True, text=True, check=True)

    if result.returncode == 0:
        # Charger les données JSON dans une variable Python
        projects = json.loads(result.stdout)

        # Parcourir les objets pour trouver celui qui correspond au critère
        for project in projects:
            if keyword in project.get("path_with_namespace", ""):
                project_id = project.get("id")
                return project_id

        print("Aucun projet correspondant trouvé.")
        return None
    else:
        print("Échec de la requête à l'API.")
        print("Erreur :", result.stderr)
        return None
