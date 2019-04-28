"""

# tests/test_xref.py

"""

import logging
import random
import sys
import unittest

from playermatcher.xref import Site
from nflmisc.nflpg import getdb
from sportscraper.utility import rand_dictitem


logger = logging.getLogger()
logger.level = logging.INFO


class Site_test(unittest.TestCase):
    '''
    Tests xref

    '''
    def setUp(self):
        '''

        Returns:

        '''
        self.db = getdb('nfl')
        self.x = Site(db=self.db)
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)

    def test_get_based(self):
        '''

        Returns:

        '''
        players = self.x.get_based(first='name')
        player = rand_dictitem(players)
        self.assertIsInstance(players, dict)
        self.assertGreater(len(list(players.keys())), 50)
        self.assertIsInstance(player[0], str)
        self.assertIsInstance(player[1], int)
        players = self.x.get_based(first='id')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], int)
        self.assertIsInstance(player[1], str)

    def test_get_base_playernames(self):
        '''

        Returns:

        '''
        players = self.x.get_base_playernames()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 50)
        self.assertIsInstance(player, str)

    def test_get_base_players(self):
        '''

        Returns:

        '''
        players = self.x.get_base_players()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())

    def test_get_mfld(self):
        '''

        Returns:

        '''
        players = self.x.get_mfld(first='name')
        player = rand_dictitem(players)
        self.assertIsInstance(players, dict)
        self.assertGreater(len(list(players.keys())), 50)
        self.assertIsInstance(player[0], str)
        self.assertIsInstance(player[1], int)
        players = self.x.get_mfld(first='id')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], int)
        self.assertIsInstance(player[1], str)

    def test_get_mfl_playernames(self):
        '''

        Returns:

        '''
        players = self.x.get_mfl_playernames()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 50)
        self.assertIsInstance(player, str)

    def test_get_mfl_players(self):
        '''

        Returns:

        '''
        players = self.x.get_mfl_players()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertIsInstance(player, dict)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())

    def test_get_sourced(self):
        '''

        Returns:

        '''
        self.x.source_name = 'pff'
        players = self.x.get_sourced(first='name')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], str)
        self.assertIsInstance(player[1], str)

        players = self.x.get_sourced(first='id')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], str)
        self.assertIsInstance(player[1], str)

        self.x.source_name = 'xxx'
        players = self.x.get_sourced(first='name')
        self.assertFalse(bool(players))

    def test_get_source_playernames(self):
        '''

        Returns:

        '''
        self.x.source_name = 'pff'
        players = self.x.get_source_playernames()
        player = random.choice(players)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 0)
        self.assertIsInstance(player, str)

    def test_get_source_players(self):
        '''

        Returns:

        '''
        self.x.source_name = 'pff'
        players = self.x.get_source_players()
        player = random.choice(players)
        self.assertIsInstance(players, list)
        self.assertIsInstance(player, dict)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())


if __name__=='__main__':
    unittest.main()
