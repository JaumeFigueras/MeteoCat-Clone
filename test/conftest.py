import pytest
import datetime
from pytest_postgresql import factories
from pathlib import Path

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

test_folder = Path(__file__).parent
postgresql_session = factories.postgresql_proc(host='127.0.0.1',
    port=9876, user='gisfireuser')
postgresql_schema = factories.postgresql('postgresql_proc', db_name='test', load=[
    'database_init.sql',
    str(test_folder.parent) + '/database/user_access.sql',
    str(test_folder.parent) + '/database/meteocat_xdde.sql',
    'database_populate.sql'])

"""from api import create_app

@pytest.fixture
def api(postgresql_schema):
    app = create_app(postgresql_schema)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

pytest_plugins = ['fixtures.indices', 'fixtures.commodities', 'fixtures.stocks',
     'fixtures.global_matrices', 'fixtures.models_close_close', 'fixtures.fmp',
     'fixtures.api']
"""
