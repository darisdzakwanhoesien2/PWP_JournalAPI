import unittest
import logging
from src import data_store

class DataStoreTestCase(unittest.TestCase):
    def test_load_comments_and_save_comments(self):
        # Test load_comments returns a list
        comments = data_store.load_comments()
        self.assertIsInstance(comments, list)

        # Test save_comments does not raise error
        try:
            data_store.save_comments(comments)
        except Exception as e:
            self.fail(f"save_comments raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
