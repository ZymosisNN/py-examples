import sqlite3
from typing import Literal
import rm_errors


RES_TYPES = Literal['epc_node', 'enb_node', 'ue', 'webui']


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    col_names = [col[0] for col in cursor.description]
    return {k: v for k, v in zip(col_names, row)}


CON = sqlite3.connect('rm.db', isolation_level=None)
CON.row_factory = dict_factory
CON.execute('PRAGMA foreign_keys = 1')


def reserve_resource(res_type: RES_TYPES, user_name: str) -> int:
    cursor = CON.cursor()
    query = ('SELECT r.name, r.id, r.type_id '
             'FROM resource r '
             'JOIN resource_type rt ON r.type_id = rt.id '
             'WHERE r.id NOT IN (SELECT resource_id FROM reservation) '
             f'AND rt.name = "{res_type}"'
             'LIMIT 1;')
    cursor.execute(query)
    unreserved = cursor.fetchone()
    if not unreserved:
        raise rm_errors.NoFreeResource(f'Requested resource type: "{res_type}"')

    print(f'{unreserved=}')
    query = ('INSERT INTO reservation (resource_id, reserved_by) '
             'VALUES ('
             f'{unreserved["id"]}, '
             f'(SELECT id FROM user WHERE name = "{user_name}")'
             ');')
    print(f'{query=}')
    try:
        cursor.execute(query)
    except sqlite3.IntegrityError as e:
        raise rm_errors.UserNotFound(f'Username = "{user_name}"') from e

    res = cursor.fetchall()
    print(res)

    return 0


if __name__ == '__main__':
    reserve_resource('enb_node', 'k.gordeev')

