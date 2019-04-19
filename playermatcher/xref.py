'''
xref.py
class for matching players across sites

'''
from collections import defaultdict
import logging

from .match import player_match
from .name import first_last


class Site():
    '''
    Base class for matching players

    '''

    def __init__(self, db, **kwargs):
        '''

        Args:
            db(NFLPostgres): instance
            **kwargs
            
        Returns:
            Site

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.db = db
        if kwargs.get('based'):
            self.based = kwargs['based']
        else:
            self.based = {}
        if kwargs.get('mfld'):
            self.mfld = kwargs['mfld']
        else:
            self.mfld = {}
        if kwargs.get('mfl_players'):
            self.mfl_players = kwargs['mfl_players']
        else:
            self.mfl_players = {}
        if kwargs.get('player_query'):
            self.player_query = kwargs['player_query']
        else:
            self.player_query = {}
        if kwargs.get('playernames'):
            self.playernames = kwargs['playernames']
        else:
            self.playernames = {}
        if kwargs.get('players'):
            self.players = kwargs['players']
        else:
            self.players = {}
        if kwargs.get('playersd'):
            self.playersd = kwargs['playersd']
        else:
            self.playersd = {}
        if kwargs.get('site_name'):
            self.site_name = kwargs['site_name']
        else:
            self.site_name = ''

    def get_based(self,
                  first='base',
                  name_key='source_player_id'):
        '''
        Dict of player_id: source_player_id or vice versa

        Returns:
	        dict

        '''
        fields = f'player_id as m, {name_key} as s'
        q = self.player_query.format(fields)
        players = self.db.select_dict(q)
        if first == 'base':
            return {p['m']: p['s'] for p in players}
        return {p['s']: p['m'] for p in players}

    def get_base_players(self, db=None):
        '''

        Returns:
            list: of dict

        '''
        if not db:
            db = self.db
        q = 'SELECT * FROM base.player'
        return self.db.select_dict(q)

    def get_mfld(self,
                 first='mfl',
                 name_key='source_player_id'):
        '''
        Dict of mfl_player_id: source_player_id or vice versa

        Args:
            first(str):
            name_key(str):

        Returns:
            dict

        '''
        fields = f'mfl_player_id as m, {name_key} as s'
        q = self.player_query.format(fields)
        players = self.db.select_dict(q)
        if first == 'mfl':
            return {p['m']: p['s'] for p in players}
        return {p['s']: p['m'] for p in players}

    def get_mfl_players(self, db=None):
        '''
        Interface

        Returns:
            list: of dict

        '''
        if not db:
            db = self.db
        q = 'SELECT * FROM base.player WHERE mfl_player_id IS NOT NULL'
        return db.select_dict(q)

    def get_site_players(self):
        '''
        Interface

        Returns:
            list: of dict

        '''
        return self.db.select_dict(self.player_query.format('*'))

    def get_site_playersd(self,
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
        q = self.player_query.format('*')
        if dict_key == 'name':
            for p in self.db.select_dict(q):
                playersd[p[name_key]].append(p)
        elif dict_key == 'namepos':
            for p in self.db.select_dict(q):
                k = (p[name_key], p[pos_key])
                playersd[k].append(p)
        else:
            raise ValueError('invalid key name: %s', dict_key)
        return playersd

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
        if kwargs.get('based'):
            based = kwargs['based']
        else:
            based = self.get_based(first='base')
        if kwargs.get('base_players'):
            base_players = kwargs['base_players']
        else:
            base_players = self.get_base_players()
        if kwargs.get('mfld'):
            mfld = kwargs['mfld']
        else:
            mfld = self.get_mfld(first='mfl')
        if kwargs.get('mfl_players'):
            mfl_players = kwargs['mfl_players']
        else:
            mfl_players = self.get_mfl_players()
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
        if kwargs.get('mfl_playernames'):
            mfl_playernames = kwargs['mfl_playernames']
        else:
            mfl_playernames = [p['full_name'] for p in mfl_players]
        if kwargs.get('base_playernames'):
            base_playernames = kwargs['base_playernames']
        else:
            base_playernames = [p['full_name'] for p in base_players]

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
