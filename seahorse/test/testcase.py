import json
import unittest


class SimpleTestCase(unittest.TestCase):
    """
    we'll use for test client self.client
    can be overriden by derived classes
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def assertHTMLEqual(self, html1, html2, msg=None):
        pass

    def assertJSONEqual(self, raw, expected_data, msg=None):
        try:
            data =json.load(raw)
        except json.JSONDecodeError:
            self.fail("First argument is not Valid JSON: %r" % raw)
        if isinstance(expected_data, str) :
            try:
                expected_data = json.loads(expected_data)
            except ValueError:
                self.fail("Second argument %r" % expected_data)
        self.assertEqual(data, expected_data, msg=msg)
    