"""
Module to update a requirements.txt file with the latest package versions from a GitLab package registry.

This script checks all packages in a requirements.txt file that use the 'package>=version' syntax and updates them to the latest available version in the specified GitLab package registry project.

Usage:
    python update_requirements.py path/to/requirements.txt

Environment Variables:
    GITLAB_URL: URL of the GitLab instance (default: CI_SERVER_URL, otherwise https://gitlab.com)
    GITLAB_PACKAGE_REPOSITORY_PROJECT_ID: GitLab project ID for the package registry
    GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN: Private token for GitLab API access
"""
import argparse
import logging
import re
import package.settings as settings

from packaging.version import Version

from package.provider.gitlab import GitlabVersionProvider


def parse_requirements(requirements_path):
    """
    Parse a requirements.txt file and extract all packages with a ">=" version specifier.

    Args:
        requirements_path (str): Path to the requirements.txt file.

    Returns:
        tuple: (lines, entries)
            lines (list of str): All lines from the file.
            entries (list of dict): Each dict contains 'name', 'version', 'line', and 'idx'.

    Example:
        >>> lines, entries = parse_requirements('requirements.txt')
        >>> entries[0]['name']
        'ac-lib'
    """
    pattern = re.compile(r"^([a-zA-Z0-9_\-]+)\s*>=\s*([0-9a-zA-Z\.-]+)")
    with open(requirements_path, "r") as f:
        lines = f.readlines()
    entries = []
    for idx, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            entries.append({
                "name": m.group(1),
                "version": m.group(2),
                "line": line,
                "idx": idx
            })
    return lines, entries

def update_requirements(requirements_path, project_id, private_token):
    """
    Update all packages in a requirements.txt file to the latest version from the GitLab package registry.

    Args:
        requirements_path (str): Path to the requirements.txt file.
        project_id (str): GitLab project ID.
        private_token (str): GitLab API private token.

    Returns:
        None

    Example:
        >>> update_requirements('requirements.txt', '123', 'token')
    """
    logger = logging.getLogger("update_requirements")
    lines, entries = parse_requirements(requirements_path)
    provider = GitlabVersionProvider(project_id, private_token)
    updated = False
    for entry in entries:
        name = entry["name"]
        current_version = Version(entry["version"])
        latest_version = provider.get_latest_version_from_gitlab(name)
        if latest_version and latest_version > current_version:
            logger.info(f"Update {name}: {current_version} -> {latest_version}")
            new_line = re.sub(r">=\s*[0-9a-zA-Z\.-]+", f">={latest_version}", entry["line"])
            lines[entry["idx"]] = new_line
            updated = True
        else:
            logger.info(f"{name} ist aktuell (>= {current_version})")
    if updated:
        with open(requirements_path, "w") as f:
            f.writelines(lines)
        logger.info(f"{requirements_path} wurde aktualisiert.")
    else:
        logger.info("Keine Updates notwendig.")

def main():
    """
    Command-line entry point for updating a requirements.txt file.

    Parses arguments, configures logging, checks environment variables, and runs the update process.
    """
    parser = argparse.ArgumentParser(description="Aktualisiere requirements.txt mit neuesten GitLab-Package-Versionen.")
    parser.add_argument("requirements", help="Pfad zur requirements.txt")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not settings.PRIVATE_TOKEN:
        raise EnvironmentError("GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN nicht gesetzt.")
    if not settings.PROJECT_ID:
        raise EnvironmentError("GITLAB_PACKAGE_REPOSITORY_PROJECT_ID nicht gesetzt.")
    update_requirements(args.requirements, settings.PROJECT_ID, settings.PRIVATE_TOKEN)

if __name__ == "__main__":
    main()