'''

xref.py
class for matching players across sites

'''

from collections import defaultdict
import logging
import typing

import attr

from .match import player_match
from .name import first_last
from nflmisc import nflpg


def add_xref(xref_dict, base, session):
    '''
    Adds playerxref object to database

    Args:
        xref_dict(dict):
        base(sqlalchemy.base):
        session(sqlalchemy.session):

    Returns:

    '''
    PlayerXref = base.classes.player_xref
    session.add(
      PlayerXref(
        player_id=xref_dict['player_id'],
        source=xref_dict['source'],
        source_player_id=xref_dict.get('source_player_id'),
        source_player_code=xref_dict.get('source_player_code'),
        source_player_name=xref_dict['source_player_name'],
        source_player_position=xref_dict['source_player_position']
      )
    )

@attr.s(kw_only=True)
class Site:
    '''
    Base class for matching players

    '''
    db = attr.ib(type=nflpg.NFLPostgres,
                 validator=attr.validators.instance_of(nflpg.NFLPostgres))
    based = attr.ib(type=dict,
                    factory=dict,
                    validator=attr.validators.instance_of(dict))
    base_players = attr.ib(type=typing.List[dict],
                           factory=list,
                           validator=attr.validators.instance_of(list))
    base_playernames = attr.ib(type=typing.List[str],
                               factory=list,
                               validator=attr.validators.instance_of(list))
    mfld = attr.ib(type=dict,
                   factory=dict,
                   validator=attr.validators.instance_of(dict))
    mfl_players = attr.ib(type=typing.List[dict],
                           factory=list,
                           validator=attr.validators.instance_of(list))
    mfl_playernames = attr.ib(type=typing.List[str],
                               factory=list,
                               validator=attr.validators.instance_of(list))
    player_query = attr.ib(type=str,
                           default="SELECT {} FROM base.player")
    source_name = attr.ib(type=str, default='')
    sourced = attr.ib(type=dict,
                   factory=dict,
                   validator=attr.validators.instance_of(dict))
    source_players = attr.ib(type=typing.List[dict],
                           factory=list,
                           validator=attr.validators.instance_of(list))
    source_playernamepos = attr.ib(type=typing.List[tuple],
                               factory=list,
                               validator=attr.validators.instance_of(list))
    source_playernames = attr.ib(type=typing.List[str],
                               factory=list,
                               validator=attr.validators.instance_of(list))
    xref_query = attr.ib(type=str,
                         default=("SELECT {} FROM base.player_xref "
                                  "WHERE SOURCE = '{}'"))

    def __attrs_post_init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def get_based(self,
                  first='name',
                  name_key='full_name'):
        '''
        Dict of player_id: name or vice versa from base players table
        Uses default dict when key is name because of duplicates

        Returns:
	        dict(if first=id) or defaultdict(if first=name)

        '''
        fields = f'player_id as id, {name_key} as name'
        q = self.player_query.format(fields)
        players = self.db.select_dict(q)
        if first == 'name':
            self.based = defaultdict(list)
            for p in players:
                self.based[p['name']].append(p['id'])
        else:
            self.based = {p['id']: p['name'] for p in players}
        return self.based

    def get_base_players(self):
        '''
        List of player dicts from base players table

        Returns:
            list: of dict

        '''
        if not self.base_players:
            q = 'SELECT * FROM base.player'
            self.base_players = self.db.select_dict(q)
        return self.base_players

    def get_base_playernames(self):
        '''
        List of player names from base players table

        Returns:
            list: of str

        '''
        if not self.base_playernames:
            q = 'SELECT full_name FROM base.player'
            self.base_playernames = self.db.select_dict(q)
        return self.base_playernames

    def get_mfld(self,
                  first='name',
                  name_key='full_name'):
        '''
        Dict of mfl_player_id: name or vice versa from base player table
        Uses default dict when key is name because of duplicates

        Returns:
	        dict(if first=id) or defaultdict(if first=name)

        '''
        q = """SELECT mfl_player_id as id, full_name as name
               FROM base.player 
               WHERE mfl_player_id IS NOT NULL"""
        players = self.db.select_dict(q)
        if first == 'name':
            self.mfld = defaultdict(list)
            for p in players:
                self.mfld[p['name']].append(p['id'])
        else:
            self.mfld = {p['id']: p['name'] for p in players}
        return self.mfld

    def get_mfl_playernames(self):
        '''
        List of names from base players table that have mfl id

        Returns:
            list: of dict

        '''
        if not self.mfl_playernames:
            q = """SELECT full_name FROM base.player 
                   WHERE mfl_player_id IS NOT NULL"""
            self.mfl_playernames = self.db.select_list(q)
        return self.mfl_playernames

    def get_mfl_players(self):
        '''
        List of player dict with mfl id from base player table

        Returns:
            list: of dict

        '''
        if not self.mfl_players:
            q = """SELECT * FROM base.player 
                   WHERE mfl_player_id IS NOT NULL"""
            self.mfl_players = self.db.select_dict(q)
        return self.mfl_players

    def get_sourced(self, first='name'):
        '''
        Dict of source name: id or vice versa from xref table

        Args:
            first(str): 'name' or 'id'
            Uses default dict when key is name because of duplicates

        Returns:
	        dict(if first=id) or defaultdict(if first=name)

        '''
        q = """SELECT source_player_id as id, 
               source_player_name as name
               FROM base.player_xref 
               WHERE source ='{}'"""
        players = self.db.select_dict(q.format(self.source_name))
        if first == 'name':
            self.sourced = defaultdict(list)
            for p in players:
                self.sourced[p['name']].append(p['id'])
        elif first == 'id':
            self.sourced = {p['id']: p['name'] for p in players}
        else:
            raise ValueError('invalid value for first %s' % first)
        return self.sourced

    def get_source_players(self):
        '''
        Interface

        Returns:
            list: of dict

        '''
        if not self.source_players:
            self.source_players = self.db.select_dict(self.xref_query.format('*', self.source_name))
        return self.source_players

    def get_source_playernamepos(self,
                                 name_key='source_player_name',
                                 pos_key='source_player_position'):
        '''
        List of tuples of site playername and position.

        Args:
            name_key(str): default 'source_player_name'
            pos_key(str): default 'source_player_position'

        Returns:
            list: of tuples

        '''
        if not self.source_playernamepos:
            fields = f'{name_key} as name, {pos_key} as pos'
            q = self.xref_query.format(fields, self.source_name)
            self.source_playernamepos = [(p['name'], p['pos']) for
                                       p in self.db.select_dict(q)]
        return self.source_playernamepos

    def get_source_playernames(self, name_key='source_player_name'):
        '''
        List of site playernames.

        Args:
            name_key(str): default 'source_player_name'

        Returns:
            list

        '''
        if not self.source_playernames:
            q = self.xref_query.format(name_key, self.source_name)
            self.source_playernames = self.db.select_list(q)
        return self.source_playernames

    def make_source_based(self,
                          source_keys,
                          dict_key='name',
                          name_key='full_name',
                          pos_key='primary_pos'):
        '''
        Creates defaultdict matching site players/playerpos
         to values in the base player table

        Args:
            source_keys(list): keys to use to match player name/namepos
            dict_key(str): 'name' or 'namepos'
            name_key(str): default 'full_name'
            pos_key(str): default 'primary_position'

        Returns:
            dict

        Examples:
            source_based = xr.get_source_based(source_keys=source_playernames)
            {'Joe Thomas': [{Joe Thomas 1 dict}, {Joe Thomas 2 dict}]

            source_based = xr.get_source_based(source_keys=source_playernames,
                                               dict_key='namepos')
            {('Michael Thomas', 'WR'): [{Michael Thomas WR 1 dict},
                                   {Michael Thomas WR 2 dict}]

        '''
        source_based = {}
        base_players = self.get_base_players()
        if dict_key == 'name':
            # match source players and base players
            for key in source_keys:
                matches = [p for p in base_players
                           if p[name_key] == key]
                if matches:
                    source_based[key] = matches
        elif dict_key == 'namepos':
            for key in source_keys:
                matches = [p for p in base_players
                           if key == (p[name_key], p[pos_key])]
                if matches:
                    source_based[key] = matches
        else:
            raise ValueError('invalid key name: %s', dict_key)
        return source_based

    def make_source_mfld(self,
                          source_keys,
                          dict_key='name',
                          name_key='full_name',
                          pos_key='primary_pos'):
        '''
        Creates defaultdict matching mfl players/playerpos
         to values in the base player table

        Args:
            source_keys(list): keys to use to match player name/namepos
            dict_key(str): 'name' or 'namepos'
            name_key(str): default 'full_name'
            pos_key(str): default 'primary_position'

        Returns:
            dict

        Examples:
            source_based = xr.get_source_based(source_keys=source_playernames)
            {'Joe Thomas': [{Joe Thomas 1 dict}, {Joe Thomas 2 dict}]

            source_based = xr.get_source_based(source_keys=source_playernames,
                                               dict_key='namepos')
            {('Michael Thomas', 'WR'): [{Michael Thomas WR 1 dict},
                                   {Michael Thomas WR 2 dict}]

        '''
        source_based = {}
        mfl_players = self.get_mfl_players()
        if dict_key == 'name':
            # match source players and base players
            for key in source_keys:
                matches = [p for p in mfl_players
                           if p[name_key] == key]
                if matches:
                    source_based[key] = matches
        elif dict_key == 'namepos':
            for key in source_keys:
                matches = [p for p in mfl_players
                           if key == (p[name_key], p[pos_key])]
                if matches:
                    source_based[key] = matches
        else:
            raise ValueError('invalid key name: %s', dict_key)
        return source_based

    def match_base(self,
                   players_to_match,
                   name_key='source_player_name'):
        """
        Adds player_id to list of players

        Args:
            players_to_match(list):
            name_key(str): default 'source_player_name'

        Returns:
            list of dict, dict of list, list of dict

        """
        duplicates = {}
        unmatched = []

        base_players = self.get_base_players()
        for idx, p in enumerate(players_to_match):
            # first option is to see if already in database
            # if that fails, use player_match routine
            matches = [bp for bp in base_players if
                       p[name_key] == bp['full_name']]
            if matches and len(matches) == 1:
                logging.info('direct match %s' % p[name_key])
                match = matches[0]
                players_to_match[idx]['player_id'] = match['player_id']
            elif matches and len(matches) > 1:
                logging.info('duplicate match %s' % p[name_key])
                duplicates[p[name_key]] = matches
            else:
                logging.info('no match %s' % p[name_key])
                unmatched.append(p)
        return players_to_match, duplicates, unmatched

    def match_mfl(self,
                   players_to_match,
                   name_key='source_player_name'):
        """
        Adds mfl_player_id to list of players

        Args:
            players_to_match(list):
            name_key(str): default 'source_player_name'

        Returns:
            list of dict, dict of list, list of dict

        """
        duplicates = {}
        unmatched = []

        mfl_players = self.get_mfl_players()
        for idx, p in enumerate(players_to_match):
            # first option is to see if already in database
            # if that fails, use player_match routine
            matches = [bp for bp in mfl_players if
                       p[name_key] == bp['full_name']]
            if matches and len(matches) == 1:
                logging.info('direct match %s' % p[name_key])
                match = matches[0]
                players_to_match[idx]['mfl_player_id'] = \
                    match['mfl_player_id']
            elif matches and len(matches) > 1:
                logging.info('duplicate match %s' % p[name_key])
                duplicates[p[name_key]] = matches
            else:
                logging.info('no match %s' % p[name_key])
                unmatched.append(p)
        return players_to_match, duplicates, unmatched

    """
    def match_mfl(self, mfl_players, id_key, name_key, interactive=False):
        '''
        Matches mfl players to site players

        Args:
            mfl_players(list):
            id_key(str):
            name_key(str):
            interactive(bool):

        Returns:
            list: of player

        '''
        mfld = self.get_mfld(first='mfl')
        sited = self.get_playersd('name')
        source_playernames = list(sited.keys())

        for idx, p in enumerate(mfl_players):
            # first option is to see if already in database
            # if that fails, use player_match routine
            if mfld.get(p[id_key]):
                mfl_players[idx][id_key] = mfld[p[id_key]]
                continue
            match_name = player_match(first_last(p[name_key]), source_playernames, thresh=90,
                                      interactive=interactive)
            match = sited.get(match_name)
            if match and len(match) == 1:
                mfl_players[idx][id_key] = match[0][id_key]
        return mfl_players
    """



if __name__ == '__main__':
    pass
