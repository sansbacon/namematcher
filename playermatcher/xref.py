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
        Dict of player_id: source_player_id or vice versa

        Returns:
	        dict

        '''
        fields = f'player_id as id, {name_key} as name'
        q = self.player_query.format(fields)
        players = self.db.select_dict(q)
        if first == 'name':
            self.based = {p['name']: p['id'] for p in players}
        else:
            self.based = {p['id']: p['name'] for p in players}
        return self.based

    def get_base_players(self):
        '''

        Returns:
            list: of dict

        '''
        if not self.base_players:
            q = 'SELECT * FROM base.player'
            self.base_players = self.db.select_dict(q)
        return self.base_players

    def get_base_playernames(self):
        '''

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
        Dict of player_id: source_player_id or vice versa

        Returns:
            dict

        '''
        q = """SELECT mfl_player_id as id, full_name as name
               FROM base.player 
               WHERE mfl_player_id IS NOT NULL"""
        players = self.db.select_dict(q)
        if first == 'name':
            self.mfld = {p['name']: p['id'] for p in players}
        else:
            self.mfld = {p['id']: p['name'] for p in players}
        return self.mfld

    def get_mfl_playernames(self):
        '''
        Interface

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
        Interface

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
        Dict of name: id or vice versa

        Args:
            first(str): 'name' or 'id'

        Returns:
            dict

        '''
        q = """SELECT source_player_id as id, 
               source_player_name as name
               FROM base.player_xref 
               WHERE source ='{}'"""
        players = self.db.select_dict(q.format(self.source_name))
        if first == 'name':
            self.sourced = {p['name']: p['id'] for p in players}
        elif first == 'id':
            self.sourced = {p['id']: p['name'] for p in players}
        else:
            raise ValueError('invalid value for first %s' % first)
        return self.sourced


    """
    def get_sourced(self,
                    dict_key='name',
                    name_key='source_player_name',
                    pos_key='source_player_position'):
        '''
        Defaultdict of site players. Key is dict_key, value is list.

        Args:
            dict_key(str): 'name' or 'namepos'
            name_key(str): default 'source_player_name'
            pos_key(str): default 'source_player_position'

        Returns:
            dict

        '''
        playersd = defaultdict(list)
        q = self.player_query.format('*', self.source_name)
        if dict_key == 'name':
            for p in self.db.select_dict(q):
                playersd[p[name_key]].append(p)
        elif dict_key == 'namepos':
            for p in self.db.select_dict(q):
                k = (p[name_key], p[pos_key])
                playersd[k].append(p)
        else:
            raise ValueError('invalid key name: %s', dict_key)
        self.source_playersd = playersd
        return self.source_playersd
    """

    def get_source_players(self):
        '''
        Interface

        Returns:
            list: of dict

        '''
        if not self.source_players:
            self.source_players = self.db.select_dict(self.xref_query.format('*', self.source_name))
        return self.source_players

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

    def match_players(self,
                      players_to_match,
                      **kwargs):
        '''
        Adds player_id and mfl_player_id to group of players

        Args:
            players_to_match(list):
            **kwargs

        Returns:
            list: of dict

        '''
        # parse kwargs / set defaults
        if kwargs.get('id_key'):
            id_key = kwargs['id_key']
        else:
            id_key = 'source_player_id'

        if kwargs.get('name_key'):
            name_key = kwargs['name_key']
        else:
            name_key = 'source_player_name'

        if kwargs.get('interactive'):
            interactive = kwargs['interactive']
        else:
            interactive = False

        if kwargs.get('thresh'):
            thresh = kwargs['thresh']
        else:
            thresh = 90

        if kwargs.get('based'):
            based = kwargs['based']
        else:
            based = self.get_based(first='base')

        if kwargs.get('base_players'):
            base_players = kwargs['base_players']
        else:
            base_players = self.get_base_players()

        if kwargs.get('base_playernames'):
            base_playernames = kwargs['base_playernames']
        else:
            base_playernames = [p['full_name'] for p in base_players]

        if kwargs.get('mfld'):
            mfld = kwargs['mfld']
        else:
            mfld = self.get_mfld(first='mfl')

        if kwargs.get('mfl_players'):
            mfl_players = kwargs['mfl_players']
        else:
            mfl_players = self.get_mfl_players()

        if kwargs.get('mfl_playernames'):
            mfl_playernames = kwargs['mfl_playernames']
        else:
            mfl_playernames = self.get_mfl_playernames()

        for idx, p in enumerate(players_to_match):
            # MATCH MFL
            # first option is to see if already in database
            # if that fails, use player_match routine
            if mfld.get(p[id_key]):
                players_to_match[idx]['mfl_player_id'] = mfld[p[id_key]]
            else:
                match_name = player_match(first_last(p[name_key]),
                                          mfl_playernames,
                                          thresh=thresh,
                                          interactive=interactive)
                matches = [p for p in mfl_players if p['full_name'] == match_name]
                if matches and len(matches) == 1:
                    players_to_match[idx]['mfl_player_id'] = matches[0]['mfl_player_id']

            # MATCH BASE
            # first option is to see if already in database
            # if that fails, use player_match routine
            if based.get(p[id_key]):
                players_to_match[idx]['player_id'] = based[p[id_key]]
            else:
                match_name = player_match(first_last(p[name_key]),
                                          base_playernames,
                                          thresh=thresh,
                                          interactive=interactive)
                matches = [p for p in base_players if p['full_name'] == match_name]
                if matches and len(matches) == 1:
                    players_to_match[idx]['player_id'] = matches[0]['player_id']
        return players_to_match


if __name__ == '__main__':
    pass
