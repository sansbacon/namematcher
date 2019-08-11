"""

# tests/test_db.py

"""

import logging
from subprocess import check_output
import sys
import unittest

import sqlalchemy
from sqlalchemy.orm import Session

from playermatcher.db import setup


logger = logging.getLogger()
logger.level = logging.ERROR


class Db_test(unittest.TestCase):
    """
    Tests db

    """
    def setUp(self):
        """

        Returns:

        """
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)


    def test_setup(self):
        """

        Returns:

        """
        dbname = 'sqlite'
        dbfile = '../namematcher.sqlite'
        Base, eng, session = setup(database=dbname,
                                   database_file=dbfile)
        self.assertIsInstance(eng, sqlalchemy.engine.base.Engine)
        self.assertIsInstance(session, Session)
        self.assertIsInstance(Base, sqlalchemy.ext.declarative.api.DeclarativeMeta)

        dbname = 'pg'
        url = check_output(['pg_tmp', '-t', '-w', '10'])
        Base, eng, session = setup(connstr=url.decode("utf-8"),
                                   database=dbname)
        self.assertIsInstance(eng, sqlalchemy.engine.base.Engine)
        self.assertIsInstance(session, Session)
        self.assertIsInstance(Base, sqlalchemy.ext.declarative.api.DeclarativeMeta)
        session.close_all()
        eng.dispose()


if __name__=='__main__':
    unittest.main()
