""" Package Version Provider"""


import package.settings as settings
import toml
from packaging.version import Version


class PackageVersionProvider:
    """Class to read and write the version from and to pyproject.toml."""

    def __init__(self, project_file: str):
        self.project_file = project_file
        self.gitlab_url = settings.GITLAB_URL
        self.project_id = settings.PROJECT_ID

    def get_version_name_from_pyproject(self) -> tuple[Version, str]:
        """Read the version from pyproject.toml."""
        with open(self.project_file, "r") as f:
            pyproject_data = toml.load(f)

        if "project" not in pyproject_data:
            raise ValueError(f"Invalid pyproject.toml format: {self.project_file}")

        if "version" not in pyproject_data["project"]:
            raise ValueError(f"Version not found in pyproject.toml: {self.project_file}")
        version_str = pyproject_data["project"]["version"]
        version = Version(version_str)
        name = pyproject_data["project"]["name"]

        return version, name

    def set_version_in_pyproject(self, new_version: Version):
        """Update the version in pyproject.toml."""
        with open(self.project_file, "r") as f:
            pyproject_data = toml.load(f)
        pyproject_data["project"]["version"] = str(new_version)
        with open(self.project_file, "w") as f:
            toml.dump(pyproject_data, f)

    def increase_patch_level(self, version: Version) -> Version:
        """Increase the patch level of a version."""
        # Extrahiere Major, Minor und Patch
        major = version.major
        minor = version.minor
        patch = version.micro  # 'micro' entspricht dem Patch-Level

        # Erhöhe den Patch-Level
        new_patch = patch + 1

        # Erstelle eine neue Version mit dem erhöhten Patch-Level
        new_version = Version(f"{major}.{minor}.{new_patch}")
        return new_version