''' get the latest version of a package from gitlab and update the version in pyproject.toml'''

import os
import argparse
# python packet manager

from package.provider.package import PackageVersionProvider
from package.provider.gitlab import GitlabVersionProvider
import package.settings as settings


def main():
    parser = argparse.ArgumentParser(description="Aktualisiere pyproject.toml mit neuester GitLab-Package-Version.")
    parser.add_argument("pyproject", help="Pfad zur pyproject.toml")
    args = parser.parse_args()
    pyproject_file = args.pyproject

    # Check if all required environment variables are set
    if not settings.PRIVATE_TOKEN:
        raise EnvironmentError("Environment variable 'GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN' is not set.")
    if not settings.PROJECT_ID:
        raise EnvironmentError("Environment variable 'GITLAB_PACKAGE_REPOSITORY_PROJECT_ID' is not set.")

    # Initialize the version provider
    gitlab_version_provider = GitlabVersionProvider(settings.PROJECT_ID, settings.PRIVATE_TOKEN)
    package_version_provider = PackageVersionProvider(pyproject_file)

    pyproject_version, pyproject_name = package_version_provider.get_version_name_from_pyproject()
    gitlab_version = gitlab_version_provider.get_latest_version_from_gitlab(pyproject_name)

    print(f"GitLab version: {gitlab_version}")
    print(f"pyproject.toml version: {pyproject_version}")

    if gitlab_version >= pyproject_version:
        new_version = package_version_provider.increase_patch_level(gitlab_version)
        print(f"Updating pyproject.toml version to: {new_version}")
        package_version_provider.set_version_in_pyproject(new_version)
    else:
        print("pyproject.toml version is up-to-date.")

if __name__ == "__main__":
    main()