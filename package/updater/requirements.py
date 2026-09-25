""" The RequirementsUpdater class is used to update the versions of packages in a requirements.txt file. """

from typing import Any
from package.provider.gitlab import GitlabVersionProvider


from packaging.version import Version


import logging
import re


class RequirementsUpdater:
    """
    The RequirementsUpdater class is used to update the versions of packages in a requirements.txt file.
    It checks all packages in the file that use the 'package>=version' syntax and updates them to the latest available version in the specified GitLab package registry project.
    """

    def __init__(self, private_token:str, project_id:str):
        """
        Initialize the RequirementsUpdater with GitLab project ID and private token.

        Args:
            project_id (str): GitLab project ID.
            private_token (str): GitLab API private token.
        """
        self.private_token = private_token
        self.project_id = project_id
        self.provider = GitlabVersionProvider(project_id, private_token)


    def update_requirements(self, requirements_path:str):
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
        lines, entries = self.parse_requirements(requirements_path)
        updated = False
        for entry in entries:
            name = entry["name"]
            current_version = Version(entry["version"])
            latest_version = self.provider.get_latest_version_from_gitlab(name)
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


    @staticmethod
    def parse_requirements(requirements_path:str) -> tuple[list[str], list[dict[str, Any]]]:
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
