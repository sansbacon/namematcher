# -*- coding: utf-8 -*-
# test_name_mflxref.py

import logging
import random
import sys
import unittest

from namematcher.name import *

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Name_test(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.names = ['Joe Thomas', 'Thomas Johnson', 'Thomas Joseph',
                         'Joseph Thime', 'Timmy Johnson']

    @property
    def name(self):
        return random.choice(self.names)

    def test_first_last(self):
        fl = first_last('Thomas, Joe')
        self.assertEqual(fl, 'Joe Thomas')
        fl = first_last('John Smith Jr.')
        self.assertEqual(fl, 'John Smith')

    def test_last_first(self):
        fl = last_first('Joe Thomas')
        self.assertEqual(fl, 'Thomas, Joe')
        fl = last_first('John Smith Jr.')
        self.assertEqual(fl, 'Smith, John')

    def test_first_last_pair(self):
        fl = first_last_pair('Thomas, Joe')
        self.assertEqual(fl, ('Joe', 'Thomas'))
        fl = first_last_pair('John Smith Jr.')
        self.assertEqual(fl, ('John', 'Smith'))

    def test_namestrip(self):
        pl = self.name
        for char in ['Jr.', 'III', 'IV', 'II', "'", '.', ', ', ',']:
            self.assertEqual(namestrip(pl + char), pl)


if __name__=='__main__':
    unittest.main()
