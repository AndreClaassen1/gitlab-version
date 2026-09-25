import os
import unittest
from unittest.mock import patch, Mock
from packaging.version import Version
from package.provider.gitlab import GitlabVersionProvider
from package.provider.package import PackageVersionProvider
from support import get_testdata_path, get_scratch_path

PROJECT_ID = os.getenv("GITLAB_PACKAGE_REPOSITORY_PROJECT_ID", default="123") 
PRIVATE_TOKEN = os.getenv("GITLAB_PACKAGE_REPOSITORY_ACCESS_TOKEN")

class TestPackageProvider(unittest.TestCase):
    ''' Test class for package version management.
    This class contains unit tests for the PackageVersionProvider and GitlabVersionProvider classes.
    It tests the functionality of retrieving and updating package versions in a pyproject.toml file,
    as well as retrieving the latest version from a GitLab repository.
    '''

    def setUp(self) -> None:
        # Copy `pyproject.toml` from testdata_path to scratch_path because the testdata_path is read-only
        # and the test modifies the file.
        self.scratch_pyproject_file = get_scratch_path() + "/pyproject.toml"
        with open(get_testdata_path() + "/pyproject.toml", "r") as src, open(self.scratch_pyproject_file, "w") as dst:
            dst.write(src.read())

        self.test_version_provider = PackageVersionProvider(self.scratch_pyproject_file)
        self.gitlab_version_provider = GitlabVersionProvider(PROJECT_ID, PRIVATE_TOKEN) # type: ignore

    def test_get_version_and_name_from_pyconfig(self):
        """Test if the version and name are correctly retrieved from pyproject.toml."""

        version, name = self.test_version_provider.get_version_name_from_pyproject()
        self.assertEqual(version, Version("0.1.0"))
        self.assertEqual(name, "habitica")
    
    @patch("package.provider.gitlab.requests.get")
    def test_gitlab_version_provider(self, mock_get):
        """Test if the GitLab version provider retrieves the correct version out of an unsorted list."""
        # Mock die Antwort von requests.get
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = [
            {"version": "0.1.9", "name": "habitica"},
            {"version": "0.1.10", "name": "habitica"},
            {"version": "0.1.8", "name": "habitica"},
            {"version": "0.1.7", "name": "other_package"},
        ]

        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = []

        # Funktion als side_effect, die die Antworten basierend auf dem Aufrufzähler zurückgibt
        def side_effect(*args, **kwargs):
            if mock_get.call_count == 1:
                return mock_response_1
            return mock_response_2

        mock_get.side_effect = side_effect
        latest_version = self.gitlab_version_provider.get_latest_version_from_gitlab("habitica")
        self.assertEqual(latest_version, Version("0.1.10"), "Latest version of habitica should equal to 0.1.10")


    def test_increase_version(self):
        """Test if the version is correctly increased."""
        new_version = self.test_version_provider.increase_patch_level(Version("0.1.0"))
        self.assertEqual(new_version, Version("0.1.1"), "Version should be increased to 0.1.1")

    def test_set_version_in_pyproject(self):
        """Test if the version is correctly set in pyproject.toml."""
        self.test_version_provider.set_version_in_pyproject(Version("0.1.1"))
        version, name = self.test_version_provider.get_version_name_from_pyproject()
        self.assertEqual(version, Version("0.1.1"), "Version should be set to 0.1.1")
    
    def tearDown(self) -> None:
        # Remove the scratch pyproject.toml file after the test
        if os.path.exists(self.scratch_pyproject_file):
            os.remove(self.scratch_pyproject_file)