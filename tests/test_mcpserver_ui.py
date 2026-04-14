import unittest

from fastapi.testclient import TestClient

from src.infrastructure.adapters.web import fastapi_app as web


class TestMcpserverUI(unittest.TestCase):
    def setUp(self):
        self._original_allowed = web.settings.allowed_ips
        web.settings.allowed_ips = ["*"]
        self.client = TestClient(web.app)

    def tearDown(self):
        web.settings.allowed_ips = self._original_allowed

    def test_get_mcpserver_returns_html_page(self):
        response = self.client.get("/mcpserver")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        body = response.text
        self.assertIn("GLPI MCP — Procesamiento de correos", body)
        self.assertIn("gmailBatchApp", body)
        self.assertIn("/gmail-batch/stream", body)

    def test_trailing_slash_also_works(self):
        response = self.client.get("/mcpserver/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
