import unittest
from unittest.mock import patch
import os
from config import API_URL, TOKEN_FILE, REQUEST_TIMEOUT

class TestConfig(unittest.TestCase):
    @patch.dict("os.environ", {"API_URL": "http://test-api:8000", "REQUEST_TIMEOUT": "10"})
    def test_config_with_env_vars(self):
        with patch("config.load_dotenv"):
            import config
            self.assertEqual(config.API_URL, "http://test-api:8000")
            self.assertEqual(config.REQUEST_TIMEOUT, 10)
            self.assertEqual(config.TOKEN_FILE, os.path.expanduser("~/.journal_token"))

    @patch.dict("os.environ", {})
    def test_config_default_values(self):
        with patch("config.load_dotenv"):
            import config
            self.assertEqual(config.API_URL, "http://localhost:5000/api")
            self.assertEqual(config.REQUEST_TIMEOUT, 5)
            self.assertEqual(config.TOKEN_FILE, os.path.expanduser("~/.journal_token"))

if __name__ == "__main__":
    unittest.main()