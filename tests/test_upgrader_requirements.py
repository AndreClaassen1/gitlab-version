import unittest
from unittest.mock import patch, Mock
from packaging.version import Version
import tempfile
import os
from package.updater.requirements import RequirementsUpdater

def write_temp_requirements(content):
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path

class TestUpdateRequirements(unittest.TestCase):

    def setUp(self):
        self.updater = RequirementsUpdater("token", "pid")

    @patch("package.provider.gitlab.GitlabVersionProvider.get_latest_version_from_gitlab")
    def test_update_single_package(self, mock_get_latest_version):
        # Simuliere ein Update für ein Paket
        req_content = "ac-lib>=0.1.0\n"
        path = write_temp_requirements(req_content)
        mock_get_latest_version.return_value = Version("0.2.0")
        self.updater.update_requirements(path)
        with open(path) as f:
            lines = f.readlines()
        self.assertIn("ac-lib>=0.2.0", lines[0])
        os.remove(path)

    @patch("package.provider.gitlab.GitlabVersionProvider.get_latest_version_from_gitlab")
    def test_no_update_needed(self, mock_get_latest_version):
        req_content = "ac-lib>=0.2.0\n"
        path = write_temp_requirements(req_content)
        mock_get_latest_version.return_value = Version("0.2.0")
        self.updater.update_requirements(path)
        with open(path) as f:
            lines = f.readlines()
        self.assertIn("ac-lib>=0.2.0", lines[0])
        os.remove(path)

    @patch("package.provider.gitlab.GitlabVersionProvider.get_latest_version_from_gitlab")
    def test_multiple_packages(self, mock_get_latest_version):
        req_content = "ac-lib>=0.1.0\nnotion-api-support>=0.1.0\n"
        path = write_temp_requirements(req_content)

        def side_effect(name):
            return Version("0.2.0") if name == "ac-lib" else Version("0.1.0")

        mock_get_latest_version.side_effect = side_effect
        self.updater.update_requirements(path)
        with open(path) as f:
            lines = f.readlines()
        self.assertIn("ac-lib>=0.2.0", lines[0])
        self.assertIn("notion-api-support>=0.1.0", lines[1])
        os.remove(path)

    def test_no_matching_lines(self):
        req_content = "validators==0.34.0\n# comment line\n"
        path = write_temp_requirements(req_content)
        self.updater.update_requirements(path)
        with open(path) as f:
            lines = f.readlines()
        self.assertIn("validators==0.34.0", lines[0])
        os.remove(path)

if __name__ == "__main__":
    unittest.main()
