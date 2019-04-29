"""

# tests/test_xref.py

"""

from collections import defaultdict
import logging
import random
import sys
import unittest

from playermatcher.xref import Site
from nflmisc.nflpg import getdb
from sportscraper.utility import rand_dictitem


logger = logging.getLogger()
logger.level = logging.ERROR


class Site_test(unittest.TestCase):
    """
    Tests xref

    """
    def setUp(self):
        """

        Returns:

        """
        self.db = getdb('nfl')
        self.x = Site(db=self.db)
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)

    def test_get_based(self):
        """

        Returns:

        """
        players = self.x.get_based(first='name')
        rand_key = random.choice(list(players.keys()))
        player = players[rand_key]
        self.assertIsInstance(players, defaultdict)
        self.assertIsInstance(player[0], int)
        players = self.x.get_based(first='id')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], int)
        self.assertIsInstance(player[1], str)

    def test_get_base_playernames(self):
        """

        Returns:

        """
        players = self.x.get_base_playernames()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 50)
        self.assertIsInstance(player, str)

    def test_get_base_players(self):
        """

        Returns:

        """
        players = self.x.get_base_players()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())

    def test_get_mfld(self):
        """

        Returns:

        """
        players = self.x.get_mfld(first='name')
        rand_key = random.choice(list(players.keys()))
        player = players[rand_key]
        self.assertIsInstance(players, defaultdict)
        self.assertIsInstance(player[0], int)
        players = self.x.get_mfld(first='id')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], int)
        self.assertIsInstance(player[1], str)

    def test_get_mfl_playernames(self):
        """

        Returns:

        """
        players = self.x.get_mfl_playernames()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 50)
        self.assertIsInstance(player, str)

    def test_get_mfl_players(self):
        """

        Returns:

        """
        players = self.x.get_mfl_players()
        player = random.choice(players)
        logging.info(player)
        self.assertIsInstance(players, list)
        self.assertIsInstance(player, dict)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())

    def test_get_sourced(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        players = self.x.get_mfld(first='name')
        rand_key = random.choice(list(players.keys()))
        player = players[rand_key]
        self.assertIsInstance(players, defaultdict)
        self.assertIsInstance(player[0], int)

        players = self.x.get_sourced(first='id')
        player = rand_dictitem(players)
        self.assertIsInstance(player[0], str)
        self.assertIsInstance(player[1], str)

        self.x.source_name = 'xxx'
        players = self.x.get_sourced(first='name')
        self.assertFalse(bool(players))

    def test_get_source_playernamepos(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        players = self.x.get_source_playernamepos()
        player = random.choice(players)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 0)
        self.assertIsInstance(player, tuple)
        self.assertIsInstance(player[0], str)
        self.assertIsInstance(player[1], str)
        logging.info(player)

    def test_get_source_playernames(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        players = self.x.get_source_playernames()
        player = random.choice(players)
        self.assertIsInstance(players, list)
        self.assertGreater(len(players), 0)
        self.assertIsInstance(player, str)

    def test_get_source_players(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        players = self.x.get_source_players()
        player = random.choice(players)
        self.assertIsInstance(players, list)
        self.assertIsInstance(player, dict)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())


    def test_make_source_based(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        source_keys = self.x.get_source_playernames()
        source_based = self.x.make_source_based(source_keys)
        self.assertIsInstance(source_based, dict)
        self.assertIsInstance(list(source_based.values())[0], list)

        self.x.source_name = 'pff'
        source_keys = self.x.get_source_playernamepos()
        source_based = self.x.make_source_based(source_keys,
                                                dict_key='namepos')
        self.assertIsInstance(source_based, dict)
        try:
            self.assertIsInstance(list(source_based.values())[0], list)
        except:
            self.assertIsFalse(bool(source_based))


    def test_make_source_mfld(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        source_keys = self.x.get_source_playernames()
        source_mfld = self.x.make_source_mfld(source_keys)
        self.assertIsInstance(source_mfld, dict)
        self.assertIsInstance(list(source_mfld.values())[0], list)

        self.x.source_name = 'pff'
        source_keys = self.x.get_source_playernamepos()
        source_based = self.x.make_source_mfld(source_keys,
                                                dict_key='namepos')
        self.assertIsInstance(source_based, dict)
        try:
            self.assertIsInstance(list(source_mfld.values())[0], list)
        except:
            self.assertIsFalse(bool(source_based))

    def test_match(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        to_match = self.x.get_source_players()
        match_from = self.x.get_base_players()
        players, duplicates, unmatched = self.x.match(to_match,
                                                      match_from)
        self.assertIsInstance(players, list)
        self.assertGreater(len([p for p in players if p.get('player_id')]), 0)
        player = random.choice(players)
        self.assertIsInstance(player, dict)
        logging.error(duplicates)
        logging.error(unmatched)

    def test_match_base(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        to_match = self.x.get_source_players()
        players, duplicates, unmatched = self.x.match_base(to_match)
        self.assertIsInstance(players, list)
        self.assertGreater(len([p for p in players if p.get('player_id')]), 0)
        player = random.choice(players)
        self.assertIsInstance(player, dict)
        logging.error(duplicates)
        logging.error(unmatched)

    def test_match_mfl(self):
        """

        Returns:

        """
        self.x.source_name = 'pff'
        to_match = self.x.get_source_players()
        players, duplicates, unmatched = self.x.match_mfl(to_match)
        self.assertIsInstance(players, list)
        self.assertGreater(len([p for p in players if p.get('mfl_player_id')]), 0)
        player = random.choice(players)
        self.assertIsInstance(player, dict)
        logging.error(duplicates)
        logging.error(unmatched)


if __name__=='__main__':
    unittest.main()
