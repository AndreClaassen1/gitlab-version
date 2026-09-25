""" GitLab Package Repository Version Provider
This module provides a class to interact with the GitLab Package Repository API
and fetch the latest version of a specified package."""

MAX_GITLAB_PAGES_COUNT = 100  # Maximum number of pages
GITLAB_PAGE_COUNT = 100 # Number of items per page


import requests
from packaging.version import Version

from package.settings import GITLAB_URL


class GitlabVersionProvider:
    """Class to interact with GitLab Package Repository."""
    def __init__(self, project_id: str, private_token: str):
        self.project_id = project_id
        self.private_token = private_token
        self.gitlab_url = GITLAB_URL
        self.headers = {"PRIVATE-TOKEN": self.private_token}
        self.packages_url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/packages"

    def get_latest_version_from_gitlab(self, package_name: str) -> Version:
        """Fetch the latest version of the package from the GitLab Package Repository."""
        packages = []
        page = 1

        while page < MAX_GITLAB_PAGES_COUNT:
            url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/packages"
            params = {"page": page, "per_page": GITLAB_PAGE_COUNT}  # Pagination parameters
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            page_data = response.json()
            print(f"Request #{page}: {url} - Page {page} - Status Code: {response.status_code}")

            if not page_data:  # Break if no more data
                break

            packages.extend(page_data)
            page += 1

        if page >= MAX_GITLAB_PAGES_COUNT:
            raise RuntimeError(f"Reached maximum page count: {MAX_GITLAB_PAGES_COUNT}")

        # Parse versions as Version objects for proper comparison
        versions = [
            Version(pkg["version"]) for pkg in packages
            if "version" in pkg and pkg["name"] == package_name
        ]

        # Return the highest version as a string, or "0.0.0" if no versions are found
        return max(versions, default=Version("0.0.0"))