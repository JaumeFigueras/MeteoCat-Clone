import datetime
import pytz
import json
import random

utc = pytz.UTC
CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!()_:;@?"
TOKEN_LENGTH = 64

def get_random_string(length):
    token = ""
    for i in range(length):
        token += CHARACTERS[random.randint(0, len(CHARACTERS) - 1)]
    return token

def get_user(connection, username, password):
    if username == '':
        return None
    sql = "SELECT token, valid_until, admin, id FROM tokens WHERE username = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (username, ))
    row = cursor.fetchone()
    if row is not None:
        if password == row[0]:
            if utc.localize(datetime.datetime.utcnow()) < row[1]:
                user = {'username': username, 'admin': row[2], 'id': row[3]}
            else:
                user = None
        else:
            user = None
    else:
        user = None
    cursor.close()
    return user

def new_user(connection, username, valid_until, is_admin=False):
    if username == '':
        return None
    sql = "SELECT id FROM tokens WHERE username = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (username, ))
    if cursor.rowcount != 0:
        cursor.close()
        return None
    token = get_random_string(TOKEN_LENGTH)
    sql = "INSERT INTO tokens (username, token, admin, valid_until) VALUES (%s, %s, %s, %s) RETURNING id"
    cursor.execute(sql, (username, token, is_admin, valid_until))
    row = cursor.fetchone()
    if row is not None:
        user = {'username': username, 'admin': is_admin, 'id': row[0], 'token':token, 'valid_until': datetime.datetime.strftime(valid_until, '%Y-%m-%dT%H:%M:%S')}
    connection.commit()
    cursor.close()
    return user

def delete_user(connection, username):
    if username == '':
        return False
    sql = "SELECT id FROM tokens WHERE username = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (username, ))
    if cursor.rowcount != 1:
        cursor.close()
        return False
    sql = "DELETE FROM tokens WHERE username = %s"
    cursor.execute(sql, (username, ))
    connection.commit()
    cursor.close()
    return True

def update_user(connection, username, valid_until):
    if username == '':
        return False
    sql = "SELECT id FROM tokens WHERE username = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (username, ))
    if cursor.rowcount != 1:
        cursor.close()
        return False
    sql = "UPDATE tokens SET valid_until = %s WHERE username = %s"
    cursor.execute(sql, (valid_until, username))
    connection.commit()
    cursor.close()
    return True

def register_access(connection, request, user):
    inet = request.remote_addr
    url = request.base_url
    method = request.method
    if user is None:
        user_id = None
    else:
        user_id = user['id']
    sql = "INSERT INTO access (token_id, ip, url, method) VALUES (%s, %s, %s, %s)"
    cursor = connection.cursor()
    cursor.execute(sql, (user_id, inet, url, method))
    connection.commit()
    cursor.close()
    return True
