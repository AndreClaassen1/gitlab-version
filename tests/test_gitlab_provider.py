import unittest
from unittest.mock import patch, Mock
from packaging.version import Version

from package.provider.gitlab import GitlabVersionProvider

class TestGitlabVersionProvider(unittest.TestCase):
    def setUp(self):
        self.provider = GitlabVersionProvider("dummy_project", "dummy_token")

    @patch("package.provider.gitlab.requests.get")
    def test_get_latest_version_found(self, mock_get):
        # Simuliere eine Seite mit mehreren Paketen, darunter das gesuchte
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.side_effect = [
            [
                {"name": "ac-lib", "version": "0.1.19"},
                {"name": "ac-lib", "version": "0.1.21"},
                {"name": "other", "version": "1.0.0"}
            ],
            [] # Ende der Seiten
        ]
        result = self.provider.get_latest_version_from_gitlab("ac-lib")
        self.assertEqual(result, Version("0.1.21"))

    @patch("package.provider.gitlab.requests.get")
    def test_get_latest_version_none_found(self, mock_get):
        # Keine passenden Pakete
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.side_effect = [
            [
                {"name": "other", "version": "1.0.0"}
            ],
            []
        ]
        result = self.provider.get_latest_version_from_gitlab("ac-lib")
        self.assertEqual(result, Version("0.0.0"))

    @patch("package.provider.gitlab.requests.get")
    def test_get_latest_version_multiple_pages(self, mock_get):
        # Mehrere Seiten, relevante Pakete auf Seite 2
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.side_effect = [
            [
                {"name": "other", "version": "1.0.0"}
            ],
            [
                {"name": "ac-lib", "version": "0.1.19"},
                {"name": "ac-lib", "version": "0.1.22"}
            ],
            []
        ]
        result = self.provider.get_latest_version_from_gitlab("ac-lib")
        self.assertEqual(result, Version("0.1.22"))

    @patch("package.provider.gitlab.requests.get")
    def test_get_latest_version_api_error(self, mock_get):
        # Simuliere HTTP-Fehler
        mock_get.return_value = Mock(status_code=500)
        mock_get.return_value.raise_for_status.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.provider.get_latest_version_from_gitlab("ac-lib")

if __name__ == "__main__":
    unittest.main()
