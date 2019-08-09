'''

db.py

setup automap classes

'''

import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


def setup(connstr = None,
          database='sqlite',
          database_file='../playermatcher.sqlite',
          schema=None):
    '''
    Automaps classes
    
    Args:
        database(str): default 'sqlite'
        database_file(str): default '../playermatcher.sqlite'
        schema(str): default None
        
    Returns:
        Base, engine, session

    '''
    if database in ['postgresql', 'postgres', 'pg']:
        if not connstr:
            db_user = os.getenv('PM_PG_USER')
            db_pwd = os.getenv('PM_PG_PWD')
            db_host = os.getenv('PM_PG_HOST')
            db_port = os.getenv('PM_PG_PORT')
            db_db = os.getenv('PM_PG_DB')

            connstr = (
                f"postgresql://{db_user}:{db_pwd}@{db_host}"
                f":{db_port}/{db_db}"
            )
    
    elif database == 'sqlite':
        if not connstr:
            connstr = f'sqlite:///{database_file}'

    eng = create_engine(connstr)
    session = Session(eng)

    # create metadata
    metadata = MetaData()
    metadata.reflect(eng)

    # create classes
    Base = automap_base(metadata=metadata)
    if schema:
        Base.metadata.reflect(bind=eng, schema=schema)
    else:
        Base.metadata.reflect(bind=eng)
    Base.prepare(eng)

    return Base, eng, session


def execproc(procname, engine, queryParams=[]):
    """
    Executes postgresql stored procedure

    Args:
        procname(str): name of the stored procedure
        engine(engine): sqlalchemy engine
        queryParams(list): in parameters for stored procedure

    Returns:
        list: of dict

    Usage:
        pivot = execproc('drbb.fn_player_scoring_pivot', eng)

    """
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        cursor.callproc(procname, queryParams)
        cols = [col.name for col in cursor.description]
        rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        connection.commit()
        return rows
    finally:
        connection.close()
