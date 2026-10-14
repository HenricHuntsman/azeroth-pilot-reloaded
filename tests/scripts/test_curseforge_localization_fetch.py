"""Regression tests for CurseForge authorization diagnostics (no network calls)."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

MODULE_PATH = Path(__file__).resolve().parents[2] / ".github" / "scripts" / "curseforge_localization_fetch.py"
spec = importlib.util.spec_from_file_location("curseforge_localization_fetch", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LocalizationExportAuthorizationTests(unittest.TestCase):
    @patch.object(module.requests, "get")
    def test_unauthorized_does_not_expose_token(self, mock_get):
        mock_get.return_value = Mock(status_code=401)
        token = "fake-secret-do-not-print"
        with self.assertRaisesRegex(RuntimeError, "CF_API_KEY") as caught:
            module.fetch_localization_export("https://example.test/export", token)
        self.assertNotIn(token, str(caught.exception))
        self.assertEqual(mock_get.call_args.kwargs["headers"]["X-Api-Token"], token)

    @patch.object(module.requests, "get")
    def test_forbidden_explains_project_permissions(self, mock_get):
        mock_get.return_value = Mock(status_code=403)
        with self.assertRaisesRegex(RuntimeError, "permissions"):
            module.fetch_localization_export("https://example.test/export", "secret")

    @patch.object(module.requests, "get")
    def test_success_returns_export_text(self, mock_get):
        mock_get.return_value = Mock(status_code=200, text='L["a"] = "b"')
        self.assertEqual(module.fetch_localization_export("https://example.test/export", "secret"), 'L["a"] = "b"')
        mock_get.return_value.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
