# gitlab-version

Small command line tools for Python packages that are published to a
[GitLab package registry](https://docs.gitlab.com/ee/user/packages/pypi_repository/).

They read the versions already present in the registry and use them to

- bump the patch version in `pyproject.toml` before a build, so every pipeline
  run publishes a new, unique version,
- raise `package>=x.y.z` pins in a `requirements.txt` to the newest version in
  the registry,
- delete old package versions from the registry and keep only the newest ones.

## Installation

```bash
pip install gitlab-version
```

Until a public release exists, install from source:

```bash
pip install git+https://github.com/AndreClaassen1/gitlab-version.git
```

Python 3.10 or newer is required.

## Commands

| Command | Module | What it does |
|---|---|---|
| `update-version` | `package.update_version` | Runs `update-pyproject pyproject.toml` and `update-requirements requirements.txt` in the current directory. |
| `update-pyproject <file>` | `package.update_pyproject` | Looks up the highest registry version of the package named in `<file>`. If it is greater than or equal to the local version, sets the local version to that registry version with the patch level increased by one. |
| `update-requirements <file>` | `package.update_requirements` | For every line of the form `name>=version`, replaces the version with the newest one found in the registry. Other lines stay untouched. |
| `delete-old-versions [--keep N]` | `package.delete_old_versions` | Deletes all but the newest `N` versions (default 1) of every package in the registry project. |

Each command can also be run as a module, for example
`python -m package.update_version`.

## Configuration

All settings come from environment variables.

| Variable | Required | Meaning |
|---|---|---|
| `GITLAB_PACKAGE_REPOSITORY_PROJECT_ID` | yes | ID of the GitLab project that hosts the package registry. |
| `GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN` | yes | Token sent as `PRIVATE-TOKEN`. It needs `read_api`, and `api` for `delete-old-versions`. |
| `GITLAB_URL` | no | Base URL of the GitLab instance, for example `https://gitlab.example.com`. |
| `CI_SERVER_URL` | no | Predefined by GitLab CI. Used when `GITLAB_URL` is not set. |

The GitLab URL is resolved in this order: `GITLAB_URL`, then `CI_SERVER_URL`,
then `https://gitlab.com`. Inside a GitLab CI job on a self hosted instance the
tools therefore talk to that instance without any extra setting.

When running the tools or tests from a source checkout, set `PYTHONPATH=.` so
that the `package` module is found. A local `.env` file is ignored by git and
can hold these variables for your editor.

## Usage in `.gitlab-ci.yml`

Store `GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN` as a masked CI/CD variable.

```yaml
variables:
  GITLAB_PACKAGE_REPOSITORY_PROJECT_ID: "34"

build_package:
  stage: build
  resource_group: publish
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  script:
    - python3 -m pip install --upgrade pip build twine gitlab-version
    - update-version
    - python3 -m build --wheel
    - python3 -m twine upload
        --repository-url "${CI_API_V4_URL}/projects/${GITLAB_PACKAGE_REPOSITORY_PROJECT_ID}/packages/pypi"
        -u gitlab-ci-token -p "${CI_JOB_TOKEN}" dist/*
```

`resource_group` keeps two pipelines from computing the same version at the
same time, which would make the second upload fail.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m unittest discover -s tests -v
```

All GitLab API calls in the tests are mocked, so no token is needed.

## License

MIT, see [LICENSE](LICENSE). The name is not covered by the license.
