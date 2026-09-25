"""
Script zum Löschen alter Python-Package-Versionen im angegebenen GitLab-Package-Repository.
Von jedem Package bleibt nur die neueste oder die angegebene Anzahl von Versionen erhalten.

Verwendung:
    python delete_old_package_versions.py [--keep N]

Environment-Variablen:
    GITLAB_URL: URL der GitLab-Instanz (default: CI_SERVER_URL, sonst https://gitlab.com)
    GITLAB_PACKAGE_REPOSITORY_PROJECT_ID: GitLab-Projekt-ID für das Package-Repository
    GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN: Private Token für GitLab-API-Zugriff
"""
import argparse
import logging
import package.settings as settings
import requests
from packaging.version import Version, parse as parse_version
from collections import defaultdict

GITLAB_API_URL = settings.GITLAB_URL + "/api/v4"


def get_all_packages(project_id, private_token):
    """Liefert alle Packages und deren Versionen im Projekt."""
    headers = {"PRIVATE-TOKEN": private_token}
    packages = []
    page = 1
    while True:
        url = f"{GITLAB_API_URL}/projects/{project_id}/packages"
        params = {"page": page, "per_page": 100}
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        packages.extend(data)
        page += 1
    return packages


def delete_package_version(project_id, package_id, private_token):
    """Löscht ein Package anhand seiner ID."""
    headers = {"PRIVATE-TOKEN": private_token}
    url = f"{GITLAB_API_URL}/projects/{project_id}/packages/{package_id}"
    resp = requests.delete(url, headers=headers)
    if resp.status_code == 204:
        logging.info(f"Package {package_id} gelöscht.")
    else:
        logging.warning(f"Fehler beim Löschen von Package {package_id}: {resp.status_code} {resp.text}")


def delete_old_versions(project_id, private_token, keep=1):
    """Löscht alte Versionen aller Packages, behält nur die neuesten 'keep' Versionen."""
    packages = get_all_packages(project_id, private_token)
    # Gruppiere nach Name
    grouped = defaultdict(list)
    for pkg in packages:
        grouped[pkg["name"]].append(pkg)
    for name, pkgs in grouped.items():
        # Sortiere nach Version absteigend
        pkgs_sorted = sorted(pkgs, key=lambda p: parse_version(p["version"]), reverse=True)
        to_delete = pkgs_sorted[keep:]
        for pkg in to_delete:
            logging.info(f"Lösche {name}=={pkg['version']} (ID: {pkg['id']})")
            delete_package_version(project_id, pkg["id"], private_token)
        if not to_delete:
            logging.info(f"{name}: Keine alten Versionen zu löschen.")


def main():
    parser = argparse.ArgumentParser(description="Löscht alte Package-Versionen im GitLab-Package-Repository.")
    parser.add_argument("--keep", type=int, default=1, help="Anzahl der zu behaltenden Versionen pro Package (Default: 1)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not settings.PRIVATE_TOKEN:
        raise EnvironmentError("GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN nicht gesetzt.")
    if not settings.PROJECT_ID:
        raise EnvironmentError("GITLAB_PACKAGE_REPOSITORY_PROJECT_ID nicht gesetzt.")
    delete_old_versions(settings.PROJECT_ID, settings.PRIVATE_TOKEN, keep=args.keep)

if __name__ == "__main__":
    main()
