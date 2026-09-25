'''Führt update_pyproject und update_requirements mit Standarddateien aus.'''

from package.update_pyproject import main as update_pyproject_main
from package.update_requirements import main as update_requirements_main
import sys


def main():
    # update pyproject.toml
    sys.argv = ["update_pyproject.py", "pyproject.toml"]
    update_pyproject_main()
    # update requirements.txt
    sys.argv = ["update_requirements.py", "requirements.txt"]
    update_requirements_main()

if __name__ == "__main__":
    main()
