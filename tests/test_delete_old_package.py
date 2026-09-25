import unittest
from unittest.mock import patch, MagicMock
import package.delete_old_versions as dov

class TestDeleteOldPackageVersions(unittest.TestCase):
    def setUp(self):
        self.project_id = "123"
        self.private_token = "token"

    @patch("package.delete_old_versions.get_all_packages")
    @patch("package.delete_old_versions.delete_package_version")
    def test_delete_old_versions_keep_1(self, mock_delete, mock_get_all):
        # Simuliere 3 Versionen für ein Package
        mock_get_all.return_value = [
            {"id": 1, "name": "mypkg", "version": "1.0.0"},
            {"id": 2, "name": "mypkg", "version": "2.0.0"},
            {"id": 3, "name": "mypkg", "version": "3.0.0"},
        ]
        dov.delete_old_versions(self.project_id, self.private_token, keep=1)
        # Es sollten 2 alte Versionen gelöscht werden
        deleted_ids = [call[0][1] for call in mock_delete.call_args_list]
        self.assertIn(1, deleted_ids)
        self.assertIn(2, deleted_ids)
        self.assertNotIn(3, deleted_ids)
        self.assertEqual(mock_delete.call_count, 2)

    @patch("package.delete_old_versions.get_all_packages")
    @patch("package.delete_old_versions.delete_package_version")
    def test_delete_old_versions_keep_2(self, mock_delete, mock_get_all):
        mock_get_all.return_value = [
            {"id": 1, "name": "mypkg", "version": "1.0.0"},
            {"id": 2, "name": "mypkg", "version": "2.0.0"},
            {"id": 3, "name": "mypkg", "version": "3.0.0"},
        ]
        dov.delete_old_versions(self.project_id, self.private_token, keep=2)
        # Es sollte nur die älteste Version gelöscht werden
        deleted_ids = [call[0][1] for call in mock_delete.call_args_list]
        self.assertIn(1, deleted_ids)
        self.assertNotIn(2, deleted_ids)
        self.assertNotIn(3, deleted_ids)
        self.assertEqual(mock_delete.call_count, 1)

    @patch("package.delete_old_versions.get_all_packages")
    @patch("package.delete_old_versions.delete_package_version")
    def test_delete_old_versions_nothing_to_delete(self, mock_delete, mock_get_all):
        mock_get_all.return_value = [
            {"id": 1, "name": "mypkg", "version": "1.0.0"},
        ]
        dov.delete_old_versions(self.project_id, self.private_token, keep=1)
        mock_delete.assert_not_called()

    @patch("package.delete_old_versions.get_all_packages")
    @patch("package.delete_old_versions.delete_package_version")
    def test_delete_old_versions_multiple_packages(self, mock_delete, mock_get_all):
        mock_get_all.return_value = [
            {"id": 1, "name": "pkg1", "version": "1.0.0"},
            {"id": 2, "name": "pkg1", "version": "2.0.0"},
            {"id": 3, "name": "pkg2", "version": "0.1.0"},
            {"id": 4, "name": "pkg2", "version": "0.2.0"},
            {"id": 5, "name": "pkg2", "version": "0.3.0"},
        ]
        dov.delete_old_versions(self.project_id, self.private_token, keep=1)
        deleted_ids = [call[0][1] for call in mock_delete.call_args_list]
        self.assertIn(1, deleted_ids)  # pkg1 alt
        self.assertIn(3, deleted_ids)  # pkg2 alt
        self.assertIn(4, deleted_ids)  # pkg2 alt
        self.assertNotIn(2, deleted_ids)  # pkg1 neu
        self.assertNotIn(5, deleted_ids)  # pkg2 neu
        self.assertEqual(mock_delete.call_count, 3)

if __name__ == "__main__":
    unittest.main()
