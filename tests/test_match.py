# tests/test_match.py

import logging
import random
import sys
import unittest

from namematcher.match import *


def rand_dictitem(dict_to_sample):
    """
    Gets random item from dict

    Args:
        d(dict):

    Returns:
        tuple: dict key and value

    """
    k = random.choice(list(dict_to_sample.keys()))
    return (k, dict_to_sample[k])


class Match_test(unittest.TestCase):

    def setUp(self):
        self.names = ['Joe Thomas', 'Thomas Johnson', 'Thomas Joseph',
                         'Joseph Thime', 'Timmy Johnson']

    @property
    def name(self):
        return random.choice(self.names)

    def test_match_fuzzy(self):
        '''
        to_match, match_from
        returns match, conf
        '''
        nm = self.name
        match, conf = match_fuzzy(nm, self.names)
        self.assertEqual(match, nm)
        self.assertGreater(conf, 0)

    def test_name_dict(self):
        '''
        names, full_name_key, first_name_key, last_name_key
        returns defaultdict
        '''
        l = [{'full_name': 'Joe Thomas', 'pos': 'WR'},
             {'full_name': 'Tom Johnson', 'pos': 'TE'}]
        d = name_dict(l, full_name_key='full_name')
        self.assertIsInstance(d, defaultdict)

    def test_namepos_dict(self):
        '''
        names, pos_key, full_name_key, first_name_key, last_name_key
        returns defaultdict
        '''
        l = [{'full_name': 'Joe Thomas', 'pos': 'WR'},
             {'full_name': 'Tom Johnson', 'pos': 'TE'}]
        d = namepos_dict(l, full_name_key='full_name', pos_key='pos')
        self.assertIsInstance(d, defaultdict)
        key = rand_dictitem(d)[0]
        self.assertIsInstance(d[key], list)

    def test_name_match(self):

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
        nm = self.name
        match = name_match(nm,
                             self.names,
                             thresh=85,
                             interactive=False)
        self.assertEqual(match, nm)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
