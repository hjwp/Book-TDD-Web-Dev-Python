import unittest
from rome import add

class AdditionTest(unittest.TestCase):

    def test_adding_iis(self):
        self.assertEqual(add('I', 'I'), 'II')
        self.assertEqual(add('I', 'II'), 'III')

    def test_v_and_iv(self):
        self.assertEqual(add('II', 'III'), 'V')
        self.assertEqual(add('V', 'I'), 'VI')
        self.assertEqual(add('II', 'II'), 'IV')
        self.assertEqual(add('IV', 'I'), 'V')


if __name__ == '__main__':
    unittest.main()
