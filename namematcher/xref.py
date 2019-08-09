'''

xref.py
class for matching players across sites

'''

from collections import defaultdict
import logging
import typing

import attr

from .match import match_fuzzy, match_interactive


def add_xref(xref_dict, base, session):
    '''
    Adds playerxref object to database

    Args:
        xref_dict(dict):
        base(sqlalchemy base):
        session(sqlalchemy session):

    Returns:

    '''

    PlayerXref = base.classes.player_xref

    record = (
        session.query(PlayerXref) \
            .filter(PlayerXref.source_player_id == xref_dict["source_player_id"]) \
            .filter(PlayerXref.source == xref_dict["source"]) \
            .first()
    )

    record2 = (
        session.query(PlayerXref) \
            .filter(PlayerXref.source_player_id == xref_dict["source_player_id"]) \
            .filter(PlayerXref.player_id == xref_dict["player_id"]) \
            .first()
    )

    if not (record and record2):
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

row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}


@attr.s(kw_only=True)
class Site:
    '''
    Base class for matching players

    '''
    base = attr.ib()
    session = attr.ib()
    eng = attr.ib()
    based = attr.ib(type=dict,
                    factory=dict,
                    validator=attr.validators.instance_of(dict))
    base_players = attr.ib(type=typing.List[dict],
                           factory=list,
                           validator=attr.validators.instance_of(list))
    base_playernames = attr.ib(type=typing.List[str],
                               factory=list,
                               validator=attr.validators.instance_of(list))
    base_playernamepos = attr.ib(type=typing.List[tuple],
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
        self.Player = self.base.classes.player
        self.PlayerXref = self.base.classes.player_xref

    def get_based(self, first='name'):
        '''
        Dict of player_id: name or vice versa from base players table
        Uses default dict when key is name because of duplicates

        Returns:
	        dict(if first=id) or defaultdict(if first=name)

        '''
        if first == 'name':
            self.based = defaultdict(list)
            for p in self.session.query(self.Player):
                self.based[p.full_name].append(p.player_id)
        else:
            self.based = {p.player_id: p.full_name for p in
                          self.session.query(self.Player)}
        return self.based

    def get_base_playernamepos(self):
        '''
        List of tuples of base playername and position.

        Args:
            name_key(str): default 'source_player_name'
            pos_key(str): default 'source_player_position'

        Returns:
            list: of tuples

        '''
        if not self.base_playernamepos:
            self.base_playernamepos = \
                [(p.full_name, p.primary_pos)
                 for p in self.session.query(self.Player)]
        return self.base_playernamepos

    def get_base_playernames(self):
        '''
        List of player names from base players table

        Returns:
            list: of str

        '''
        if not self.base_playernames:
            self.base_playernames = [p.full_name for p in
                                     self.session.query(self.Player)]
        return self.base_playernames

    def get_base_players(self):
        '''
        List of player dicts from base players table

        Returns:
            list: of dict

        '''
        if not self.base_players:
            self.base_playernames = [row2dict(p) for p in
                                     self.session.query(self.Player)]
        return self.base_playernames

    def get_mfld(self, first='name'):
        '''
        Dict of mfl_player_id: name or vice versa from base player table
        Uses default dict when key is name because of duplicates

        Returns:
	        dict(if first=id) or defaultdict(if first=name)

        '''
        if first == 'name':
            self.mfld = defaultdict(list)
            for p in self.session.query(self.Player) \
                    .filter(self.Player.mfl_player_id > 0):
                self.mfld[p.full_name].append(p.mfl_player_id)
        else:
            self.mfld = {p.mfl_player_id: p.full_name for p in
                          self.session.query(self.Player)}
        return self.mfld

    def get_mfl_playernames(self):
        '''
        List of names from base players table that have mfl id

        Returns:
            list: of dict

        '''
        if not self.mfl_playernames:
            self.mfl_playernames = \
                [p.full_name for p in self.session.query(self.Player) \
                    .filter(self.Player.mfl_player_id > 0)]
        return self.mfl_playernames

    def get_mfl_players(self):
        '''
        List of player dict with mfl id from base player table

        Returns:
            list: of dict

        '''
        if not self.mfl_players:
            self.mfl_players = [row2dict(p) for p in
                                self.session.query(self.Player) \
                                .filter(self.Player.mfl_player_id > 0)]
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
        if first == 'name':
            self.sourced = defaultdict(list)
            for p in self.session.query(self.PlayerXref) \
                    .filter(self.PlayerXref.source == self.source_name):
                self.sourced[p.full_name].append(p.source_player_id)
        else:
            self.sourced = {p.source_player_id: p.source_player_name
                            for p in self.session.query(self.PlayerXref) \
                              .filter(self.PlayerXref.source == self.source_name)}
        return self.sourced

    def get_source_players(self):
        '''
        Interface

        Returns:
            list: of dict

        '''
        if not self.source_players:
            self.source_players = [row2dict(p) for p in
                                   self.session.query(self.PlayerXref) \
                                     .filter(self.PlayerXref.source == self.source_name)]
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
            self.source_playernamepos = \
                [(p.source_player_name, p.source_player_position)
                 for p in self.session.query(self.PlayerXref) \
                    .filter(self.PlayerXref.source == self.source_name)]
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
            self.source_playernames = [p.source_player_name for p in
                                       self.session.query(self.PlayerXref) \
                                      .filter(self.PlayerXref.source == self.source_name)]
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
            for key in source_keys:
                logging.info('starting %s', key)
                matches = [p for p in base_players
                           if key == p[name_key]]
                if matches:
                    source_based[key] = matches
        elif dict_key == 'namepos':
            for key in source_keys:
                matches = [p for p in base_players
                           if key == (p[name_key],
                                      p[pos_key])]
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
            for key in source_keys:
                logging.info('starting %s', key)
                matches = [p for p in mfl_players
                           if key == p[name_key]]
                if matches:
                    source_based[key] = matches
        elif dict_key == 'namepos':
            for key in source_keys:
                matches = [p for p in mfl_players
                           if key == (p[name_key],
                                      p[pos_key])]
                if matches:
                    source_based[key] = matches
        else:
            raise ValueError('invalid key name: %s', dict_key)
        return source_based


    def match(self,
              to_match,
              match_from,
              id_keys=('source_player_id', 'player_id'),
              name_keys=('source_player_name', 'full_name'),
              interactive=False,
              thresh=90):
        '''
        Generic match routine

        Args:
            to_match(list): of dict
            match_from(list): of dict
            id_keys(tuple): default ('source_player_id', 'player_id')
            name_keys(tuple): default ('source_player_name', 'full_name')
            interactive(bool): default False,
            thresh(int): default 90

        Returns:
            tuple: list of dict, dict of list, list of dict

        '''
        matched = []
        duplicates = {}
        unmatched = []
        id_key_to, id_key_from = id_keys
        name_key_to, name_key_from = name_keys
        playernames_from = [mf[name_key_from] for mf in match_from]

        for p in to_match:
            # first option is to see if direct match
            matches = [mf for mf in match_from if
                       p[name_key_to] == mf[name_key_from]]
            if matches and len(matches) == 1:
                logging.debug('direct match %s', p[name_key_to])
                match = matches[0]
                p[id_key_from] = match[id_key_from]
                matched.append(p)
                continue
            elif matches and len(matches) > 1:
                logging.debug('duplicate match %s', p[name_key_to])
                duplicates[p[name_key_to]] = matches
                continue

            # try interactive match
            if interactive:
                match_name, confidence = match_interactive(
                            to_match=p[name_key_to],
                            match_from=playernames_from)
                if match_name:
                    matches = [mf for mf in match_from if
                               mf[name_key_from] == match_name]
                    if matches and len(matches) == 1:
                        logging.debug('fuzzy match %s %s', (p[name_key_to], confidence))
                        match = matches[0]
                        p[id_key_from] = match[id_key_from]
                        matched.append(p)
                        continue
                    elif matches and len(matches) > 1:
                        logging.debug('duplicate match %s', p[name_key_to])
                        duplicates[p[name_key_to]] = matches
                        continue
            else:
                match_name, confidence = match_fuzzy(
                            to_match=p[name_key_to],
                            match_from=playernames_from)
                if match_name and confidence >= thresh:
                    matches = [mf for mf in match_from if
                               mf[name_key_from] == match_name]
                    if matches and len(matches) == 1:
                        logging.debug('fuzzy match %s %s', (p[name_key_to], confidence))
                        match = matches[0]
                        p[id_key_from] = match[id_key_from]
                        matched.append(p)
                        continue
                    elif matches and len(matches) > 1:
                        logging.debug('duplicate match %s', p[name_key_to])
                        duplicates[p[name_key_to]] = matches
                        continue

            # if unmatched, log and add to unmatched
            logging.debug('no match %s', p[name_key_to])
            unmatched.append(p)
        return matched, duplicates, unmatched

    def match_base(self,
                   to_match,
                   name_key_to='source_player_name',
                   interactive=False,
                   thresh=90):
        """
        Adds player_id to list of players

        Args:
            to_match(list):
            name_key_to(str): default 'source_player_name'
            interactive(bool): default False,
            thresh(int): default 90

        Returns:
            list of dict, dict of list, list of dict

        """
        name_keys = (name_key_to, 'full_name')
        id_keys = (None, 'player_id')
        return self.match(to_match,
                          match_from=self.get_base_players(),
                          name_keys=name_keys,
                          id_keys=id_keys,
                          interactive=interactive,
                          thresh=thresh)

    def match_mfl(self,
                   to_match,
                   name_key_to='source_player_name',
                   id_key_to='source_player_id',
                   interactive=False,
                   thresh=90):
        """
        Adds mfl_player_id to list of players

        Args:
            to_match(list):
            name_key_to(str): default 'source_player_name'
            id_key_to(str): default 'source_player_id'
            interactive(bool): default False,
            thresh(int): default 90

        Returns:
            list of dict, dict of list, list of dict

        """
        name_keys = (name_key_to, 'full_name')
        id_keys = (id_key_to, 'mfl_player_id')
        return self.match(to_match,
                          match_from=self.get_base_players(),
                          name_keys=name_keys,
                          id_keys=id_keys,
                          interactive=interactive,
                          thresh=thresh)


if __name__ == '__main__':
    pass
