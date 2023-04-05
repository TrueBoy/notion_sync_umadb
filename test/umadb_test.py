import unittest
import os
import sys

sys.path.insert(0,'.')

from src.db import Umadb
from src.model import *

class TestUmadb(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        dbpath = os.path.join(os.path.expanduser(
                '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
        self.db:Umadb = Umadb(dbpath)

    def test_skill_type(self):
        skill:Skill = next(self.db.get_all_skill_data())
        self.assertIsInstance(skill.id, str, "skill id should be string")
        self.assertIsInstance(skill.name, str, "skill name should be string")
        self.assertIsInstance(skill.description, str, "skill description should be string")
        self.assertIsInstance(skill.icon_id, str, "skill icon id should be string")


if __name__ == '__main__':
    unittest.main()