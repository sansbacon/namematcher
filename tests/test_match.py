# tests/test_match.py

import logging
import random
import sys
import unittest

from playermatcher.match import *
from sportscraper.utility import rand_dictitem


class Match_test(unittest.TestCase):

    def setUp(self):
        self.players = ['Joe Thomas', 'Thomas Johnson', 'Thomas Joseph',
                         'Joseph Thime', 'Timmy Johnson']

    @property
    def player(self):
        return random.choice(self.players)

    def test_match_fuzzy(self):
        '''
        to_match, match_from
        returns match, conf
        '''
        pl = self.player
        match, conf = match_fuzzy(pl, self.players)
        self.assertEqual(match, pl)
        self.assertGreater(conf, 0)

    def test_name_dict(self):
        '''
        players, full_name_key, first_name_key, last_name_key
        returns defaultdict
        '''
        l = [{'full_name': 'Joe Thomas', 'pos': 'WR'},
             {'full_name': 'Tom Johnson', 'pos': 'TE'}]
        d = name_dict(l, full_name_key='full_name')
        self.assertIsInstance(d, defaultdict)

    def test_namepos_dict(self):
        '''
        players, pos_key, full_name_key, first_name_key, last_name_key
        returns defaultdict
        '''
        l = [{'full_name': 'Joe Thomas', 'pos': 'WR'},
             {'full_name': 'Tom Johnson', 'pos': 'TE'}]
        d = namepos_dict(l, full_name_key='full_name', pos_key='pos')
        self.assertIsInstance(d, defaultdict)
        key = rand_dictitem(d)[0]
        self.assertIsInstance(d[key], list)

    def test_player_match(self):

        '''
        Tries direct match, then fuzzy match, then interactive

        Args:
            to_match(str):
            match_from(list): of str
            thresh(int): threshold for quality of match (1-100), default 90
            timeout(int): how long to wait for interactive prompt, default 2

        Returns:
            str

        '''
        pl = self.player
        match = player_match(pl,
                             self.players,
                             thresh=85,
                             interactive=False)
        self.assertEqual(match, pl)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
