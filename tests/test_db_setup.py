import unittest
from src import db_setup

class DBSetupTestCase(unittest.TestCase):
    def test_create_database(self):
        try:
            db_setup.create_database()
        except Exception as e:
            self.fail(f"create_database raised an exception: {e}")

    def test_populate_database(self):
        try:
            db_setup.populate_database()
        except Exception as e:
            self.fail(f"populate_database raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
