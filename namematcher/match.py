'''
match.py
Common cross-reference functions

'''

from collections import defaultdict
import logging
import signal

from fuzzywuzzy import process

logging.getLogger(__name__).addHandler(logging.NullHandler())


def match_name(to_match,
               match_from,
               thresh=90,
               timeout=2,
               interactive=False):
    '''
    Tries direct match, then fuzzy match, then interactive (optional)

    Args:
        to_match(str):
        match_from(list): of str
        thresh(int): threshold for quality of match (1-100), default 90
        timeout(int): how long to wait for interactive prompt, default 2
        interactive(bool):

    Returns:
        str

    '''
    # try direct match first
    # if not, go fuzzy and then interactive
    matches = [nm for nm in match_from if nm == to_match]
    if matches and len(matches) == 1:
        return matches[0]

    matches, conf = match_fuzzy(to_match, match_from)
    if conf >= thresh:
        return matches

    if interactive:
        return match_interactive(to_match, match_from, timeout=timeout)
    else:
        return None


def match_fuzzy(to_match, match_from):
    '''
    Matches player with fuzzy match

    Args:
        to_match (str): name to match
        match_from (list): list of names to match against

    Returns:
        match(str): matched name from match_from list
        confidence(int): confidence of match

    Example:
        name, conf = match_player(name, names)

    '''
    return process.extractOne(to_match, match_from)


def match_interactive(to_match,
                      match_from,
                      default=None,
                      choices=3,
                      timeout=15):
    '''
    Matches name with fuzzy match, interactive confirmation

    Args:
        to_match(str): name to match
        match_from(list): list of names to match against
        default: default value is None
        choices(int): number of matches to try
        timeout(int): seconds to wait before providing default value

    Returns:
        (str, int)

    '''
    for match in process.extract(to_match, match_from, limit=choices):
        msg = 'Matched {} to {} with conf {}: '.format(to_match, match[0], match[1])
        resp = read_input(prompt=msg, timeout=timeout, default=default)
        if resp:
            return match
        else:
            print()
    return (default, 1)


def name_dict(names,
              full_name_key=None,
              first_name_key=None,
              last_name_key=None):
    '''
    Creates a defaultdict of name: namedict

    Args:
        names(list): of dict
        full_name_key(str): default None
        first_name_key(str): default None
        last_name_key(str): default None

    Returns:
        defaultdict(list)

    '''
    d = defaultdict(list)
    if full_name_key:
        for nm in names:
            d[nm[full_name_key]].append(nm)
    elif first_name_key and last_name_key:
        for nm in names:
            k = '{} {}'.format(nm[first_name_key], nm[last_name_key])
            d[k].append(p)
    else:
        msg = 'must specify full_name_key or first_name + last_name key'
        raise ValueError(msg)
    return d


def namepos_dict(names,
                 pos_key,
                 full_name_key=None,
                 first_name_key=None,
                 last_name_key=None):
    '''
    Creates a defaultdict of name_pos: name

    Args:
        names(list): of dict
        pos_key(str): 'position', 'pos', etc.
        full_name_key(str): default None
        first_name_key(str): default None
        last_name_key(str): default None

    Returns:
        defaultdict(list)

    '''
    d = defaultdict(list)
    if full_name_key:
        for nm in names:
            k = '{}_{}'.format(nm[full_name_key], nm[pos_key])
            d[k].append(p)
    elif first_name_key and last_name_key:
        for nm in names:
            k = '{} {}_{}'.format(nm[first_name_key],
                                  nm[last_name_key], nm[pos_key])
            d[k].append(p)
    else:
        msg = 'must specify full_name_key or first_name + last_name key'
        raise ValueError(msg)
    return d

def read_input(prompt,
               timeout,
               default=None,
               timeoutmsg = None):
    '''
    Reads input with timeout

    Args:
        prompt(str): the prompt for user input
        timeout(int): seconds to wait before timing out
        timeoutmsg(str): optional message to print if timed out

    '''
    # based on https://stackoverflow.com/questions/44037060/
    # how-to-set-a-timeout-for-input
    def timeout_error(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM, timeout_error)
    signal.alarm(timeout)
    try:
        answer = input(prompt)
        signal.alarm(0)
        return answer
    except TimeoutError:
        if timeoutmsg:
            print(timeoutmsg)
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
        return default


if __name__ == '__main__':
    pass
