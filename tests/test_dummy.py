import unittest


class Testing(unittest.TestCase):
    def test_bolean(self):
        a = True
        b = True
        self.assertEqual(a, b)
