import os


# GITLAB_URL wins; inside GitLab CI the predefined CI_SERVER_URL is used as fallback.
GITLAB_URL = os.getenv("GITLAB_URL") or os.getenv("CI_SERVER_URL") or "https://gitlab.com"
PROJECT_ID = os.getenv("GITLAB_PACKAGE_REPOSITORY_PROJECT_ID")
PRIVATE_TOKEN = os.getenv("GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN")
