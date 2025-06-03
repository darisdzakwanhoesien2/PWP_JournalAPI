import unittest
from unittest.mock import patch, MagicMock
import requests
from utils import handle_error

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.response = MagicMock()
        self.error = requests.HTTPError("HTTP error")
        self.message = "Test error"

    @patch("utils.console")
    @patch("utils.logger")
    def test_handle_error_with_json(self, mock_logger, mock_console):
        self.response.json.return_value = {"error": "Bad request"}
        handle_error(self.response, self.error, self.message)
        mock_console.print.assert_called_with(f"[red]❌ {self.message}: Bad request[/red]")
        mock_logger.error.assert_called_with("%s: %s", self.message, {"error": "Bad request"})

    @patch("utils.console")
    @patch("utils.logger")
    def test_handle_error_no_json(self, mock_logger, mock_console):
        self.response.json.side_effect = requests.JSONDecodeError("Invalid JSON", "", 0)
        self.response.text = "Server error"
        handle_error(self.response, self.error, self.message)
        mock_console.print.assert_called_with(f"[red]❌ Server error: Server error[/red]")
        mock_logger.error.assert_called_with("%s: %s, %s", self.message, "Server error", self.error)

if __name__ == "__main__":
    unittest.main()