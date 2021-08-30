import pytest
from types import SimpleNamespace
import psycopg2.extras
import json
import datetime

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from database import user_access

def test_initialization(postgresql_schema):
    """Check main postgresql fixture."""
    cursor = postgresql_schema.cursor()
    cursor.execute("SELECT * FROM tokens;")
    assert cursor.rowcount == 4
    cursor.close()

def test_get_user_01(postgresql_schema):
    """Check get_user() parameters."""
    # Check empty username passed
    user = user_access.get_user(postgresql_schema, password='qwertyui156789', username='')
    assert user is None

def test_get_user_02(postgresql_schema):
    """Check correct users returned with correct data provided."""
    # Admin user with valid date
    user = user_access.get_user(postgresql_schema, 'john.doe', 'qwertyuiop123456789')
    assert user is not None
    assert user['username'] == 'john.doe'
    assert user['id'] == 1
    assert user['admin']
    # Non admin user with valid date
    user = user_access.get_user(postgresql_schema, 'jack.valid', '0123456789asdfghjkl')
    assert user is not None
    assert user['username'] == 'jack.valid'
    assert user['id'] == 3
    assert not user['admin']
    # Admin user with expired date
    user = user_access.get_user(postgresql_schema, 'john.invalid', 'qwertyuiop123456789')
    assert user is None
    # Non admin user with expires date
    user = user_access.get_user(postgresql_schema, 'jack.invalid', '12345zxcvbnm67890')
    assert user is None

def test_get_user_03(postgresql_schema):
    """Check correct users returned with incorrect passwords."""
    # Admin user with valid date
    user = user_access.get_user(postgresql_schema, 'john.doe', 'fail')
    assert user is None
    # Non admin user with valid date
    user = user_access.get_user(postgresql_schema, 'jack.valid', 'fail')
    assert user is None
    # Admin user with expired date
    user = user_access.get_user(postgresql_schema, 'john.invalid', 'fail')
    assert user is None
    # Non admin user with expires date
    user = user_access.get_user(postgresql_schema, 'jack.invalid', 'fail')
    assert user is None

def test_get_user_04(postgresql_schema):
    """Check correct users returned with incorrect username."""
    # Admin user with valid date
    user = user_access.get_user(postgresql_schema, 'fail', 'qwertyuiop123456789')
    assert user is None

def test_new_user_01(postgresql_schema):
    """Check new_user() parameters."""
    # Check with empty username params
    user = user_access.new_user(postgresql_schema, '', datetime.datetime.now())
    assert user is None
    # Check with empty admin status
    datettime_test = '2021-12-31T00:00:00'
    datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S')
    user = user_access.new_user(postgresql_schema, valid_until=datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S'), username='test')
    assert user is not None
    assert user['username'] == 'test'
    assert len(user['token']) == 64
    assert not user['admin']
    assert user['valid_until'] == datettime_test

def test_new_user_02(postgresql_schema):
    """Check new_user() with correct parameters."""
    datettime_test = '2021-12-31T00:00:00'
    datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S')
    user = user_access.new_user(postgresql_schema, valid_until=datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S'), username='test', is_admin=True)
    assert user is not None
    assert user['username'] == 'test'
    assert len(user['token']) == 64
    assert user['admin']
    assert user['valid_until'] == datettime_test

def test_new_user_03(postgresql_schema):
    """Check new_user() with an existing username."""
    datettime_test = '2021-12-31T00:00:00'
    user = user_access.new_user(postgresql_schema, valid_until=datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S'), username='jack.valid', is_admin=True)
    assert user is None

def test_delete_user_01(postgresql_schema):
    """Check delete_user() parameters."""
    assert not user_access.delete_user(postgresql_schema, '')

def test_delete_user_02(postgresql_schema):
    """Check delete_user() with an existing username."""
    assert user_access.delete_user(postgresql_schema, 'jack.invalid')

def test_delete_user_03(postgresql_schema):
    """Check delete_user() with an unexisting username."""
    assert not user_access.delete_user(postgresql_schema, 'test')

def test_update_user_01(postgresql_schema):
    """Check update_user() parameters."""
    datettime_test = '2021-12-31T00:00:00'
    assert not user_access.update_user(postgresql_schema, '', datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S'))

def test_update_user_02(postgresql_schema):
    """Check update_user() with an existent user"""
    datettime_test = '2021-12-31T00:00:00'
    assert user_access.update_user(postgresql_schema, 'jack.invalid', datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S'))
    user = user_access.get_user(postgresql_schema, 'jack.invalid', '12345zxcvbnm67890')
    assert user is not None
    assert user['username'] == 'jack.invalid'
    assert user['id'] == 4
    assert not user['admin']

def test_update_user_03(postgresql_schema):
    """Check update_user() with an unexistent user"""
    datettime_test = '2021-12-31T00:00:00'
    assert not user_access.update_user(postgresql_schema, 'test', datetime.datetime.strptime(datettime_test, '%Y-%m-%dT%H:%M:%S'))

def test_access_01(postgresql_schema):
    """Check register_access for an unauthenticaed user."""
    user = None
    request = dict({
        'remote_addr': "127.0.0.1",
        'base_url': "/test",
        'method': "GET"
    })
    assert user_access.register_access(postgresql_schema, SimpleNamespace(**request), user)
    cursor = postgresql_schema.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM access;")
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row['id'] == 1
    assert row['token_id'] is None
    assert row['ip'] == '127.0.0.1'
    assert row['url'] == '/test'
    assert row['method'] == 'GET'
    cursor.close()

def test_access_02(postgresql_schema):
    """Check register_access for an authenticaed user."""
    user = user_access.get_user(postgresql_schema, 'john.doe', 'qwertyuiop123456789')
    request = dict({
        'remote_addr': "127.0.0.1",
        'base_url': "/test",
        'method': "GET"
    })
    assert user_access.register_access(postgresql_schema, SimpleNamespace(**request), user)
    cursor = postgresql_schema.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM access;")
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row['id'] == 1
    assert row['token_id'] == 1
    assert row['ip'] == '127.0.0.1'
    assert row['url'] == '/test'
    assert row['method'] == 'GET'
    cursor.close()
