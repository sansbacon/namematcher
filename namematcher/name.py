'''
name.py
Common name functions

'''

import logging

from nameparser import HumanName

logging.getLogger(__name__).addHandler(logging.NullHandler())


def first_last(name):
    '''
    Returns name in First Last format

    Args:
        name(str)

    Returns:
        str

    '''
    hn = HumanName(name)
    return '{0} {1}'.format(hn.first, hn.last)


def first_last_pair(name):
    '''
    Returns name in First Last pair

    Args:
        name(str)

    Returns:
        tuple: of str

    '''
    hn = HumanName(name)
    return (hn.first, hn.last)


def last_first(name):
    '''
    Returns name in Last, First format

    Args:
        name(str)

    Returns:
        str

    '''

    hn = HumanName(name)
    return '{1}, {0}'.format(hn.first, hn.last)


def namestrip(nm, tostrip=None):
    '''
    Strips various characters out of name. Used for better matching.

    Args:
        nm(str):
        tostrip(list): of str

    Returns:
        str

    '''
    if not tostrip:
        tostrip = ['Jr.', 'III', 'IV', 'II', "'", '.', ', ', ',']
    for char in tostrip:
        nm = nm.replace(char, '')
    if len(nm.split()) > 0 and nm.split()[-1] == 'V':
        nm = ' '.join(nm.split()[:-1])
    return nm.strip()


if __name__ == '__main__':
    pass
