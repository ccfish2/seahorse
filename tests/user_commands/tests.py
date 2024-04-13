
from io import StringIO
from seahorse.test import SimpleTestCase
from seahorse.core import management 

class CommandTests(SimpleTestCase):

    def test_eks(self):
        io = StringIO()
        management.call_command("eks", stdout=io)
