# -*- coding: utf-8 -*-
# test_player_mflxref.py

import logging
import random
import sys
import unittest

from playermatcher.name import *

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Name_test(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.players = ['Joe Thomas', 'Thomas Johnson', 'Thomas Joseph',
                         'Joseph Thime', 'Timmy Johnson']

    @property
    def player(self):
        return random.choice(self.players)

    def test_first_last(self):
        fl = first_last('Thomas, Joe')
        self.assertEqual(fl, 'Joe Thomas')
        fl = first_last('Odell Beckham Jr.')
        self.assertEqual(fl, 'Odell Beckham')

    def test_last_first(self):
        fl = last_first('Joe Thomas')
        self.assertEqual(fl, 'Thomas, Joe')
        fl = last_first('Odell Beckham Jr.')
        self.assertEqual(fl, 'Beckham, Odell')

    def test_first_last_pair(self):
        fl = first_last_pair('Thomas, Joe')
        self.assertEqual(fl, ('Joe', 'Thomas'))
        fl = first_last_pair('Odell Beckham Jr.')
        self.assertEqual(fl, ('Odell', 'Beckham'))

    def test_namestrip(self):
        pl = self.player
        for char in ['Jr.', 'III', 'IV', 'II', "'", '.', ', ', ',']:
            self.assertEqual(namestrip(pl + char), pl)


if __name__=='__main__':
    unittest.main()
