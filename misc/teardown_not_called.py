# http://bugs.python.org/issue5538

import unittest


class TestUnit(unittest.TestCase):
    def setUp(self):
        print("Failing setup")
        raise Exception("Failing")

    def tearDown(self):
        print("Calling teardown")

    def test_check_teardown(self):
        pass


if __name__ == '__main__':
    unittest.main()
