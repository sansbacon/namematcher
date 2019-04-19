"""

# tests/test_xref.py

"""

import logging
import random
import sys
import unittest

from nflfantasy.xref import Site
from nflmisc.utility import getdb
from sportscraper.utility import rand_dictitem


class Site_test(unittest.TestCase):
    '''
    Tests xref

    '''
    def setUp(self):
        '''

        Returns:

        '''
        self.db = getdb('nfl')
        self.x = Site(self.db)

    def test_get_base_players(self):
        '''

        Returns:

        '''
        players = self.x.get_base_players()
        player = random.choice(players)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())

    def test_get_mfl_players(self):
        '''

        Returns:

        '''
        players = self.x.get_mfl_players()
        player = random.choice(players)
        self.assertGreater(len(players), 50)
        self.assertIn('mfl_player_id', player.keys())

    def test_get_based(self):
        '''

        Returns:

        '''
        self.x.player_query = "SELECT {} FROM base.player_xref WHERE source='pff'"
        based = self.x.get_based()
        self.assertIsInstance(based, dict)
        self.assertGreater(len(list(based.keys())), 50)
        item = rand_dictitem(based)
        self.assertIsInstance(item[0], int)
        self.assertIsInstance(item[1], str)

    def test_get_mfld(self):
        '''

        Returns:

        '''
        self.x.player_query = "SELECT {} FROM base.vw_pff_mfl_xref"
        mfld = self.x.get_mfld()
        self.assertIsInstance(mfld, dict)
        self.assertGreater(len(list(mfld.keys())), 50)
        item = rand_dictitem(mfld)
        self.assertIsInstance(item[0], int)
        self.assertIsInstance(item[1], str)

    def test_get_site_players(self):
        '''

        Returns:

        '''
        self.x.player_query = "SELECT {} FROM base.vw_pff_mfl_xref"
        players = self.x.get_site_players()
        player = random.choice(players)
        self.assertGreater(len(players), 50)
        self.assertIn('player_id', player.keys())

    def test_get_site_playersd(self):
        '''

        Returns:

        '''
        self.x.player_query = "SELECT {} FROM base.vw_pff_mfl_xref"
        playersd = self.x.get_site_playersd()
        self.assertGreater(len(list(playersd.keys())), 50)

    def test_match_players(self):
        '''

        Returns:

        '''
        players_to_match = self.db.select_dict("""SELECT * 
                                                  FROM base.player_xref 
                                                  WHERE source = 'pff' 
                                                  ORDER BY RANDOM() 
                                                  LIMIT 2""")
        players = self.x.match_players(players_to_match)
        self.assertEqual(len(players), 2)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
