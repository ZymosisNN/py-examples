import pymysql
from pymysql.cursors import DictCursor

# user = 'dbalib'
# password = 'dbalib'
user = 'db59'
password = 'admin'
# host = '10.7.17.32'
host = 'qadb612.scl.five9lab.com'
database = 'Five9App'
# database = 'dnis_trunk_map'


conn = pymysql.connect(host=host, user=user, password=password, database=database, cursorclass=DictCursor)

# query = 'select * from dnis_trunk_map_parser limit 10;'
# query = "SELECT last_update, trunk, grp "\
#         " FROM dnis_trunk_map_parser"\
#         " WHERE dnis='6504580818'"\
#         " AND last_update >= '$start_d'"\
#         " ORDER BY 1 DESC LIMIT 1;"

# query = ("SELECT last_update, trunk, grp "
#          "FROM dnis_trunk_map_parser "
#          "WHERE dnis='6504580818' "
#          "ORDER BY 1 DESC LIMIT 1 ")

"""
tenant это переименованный partition
tenant.id это partition_fk в других таблицах
account.id = account_fk
domain.id=domain_fk
"""

with conn.cursor() as cursor:
    query = ('SELECT dnis.name number, cat.name category, dnis.grp billing_group, '
             'd.name domain_name, (e.flags & (1 << 61) != 0) E164, '
             't.id partition_id, db_server.host cust_db_host '
             'FROM dnis '
             'JOIN tenant t ON (t.id = dnis.partition_fk) '
             'JOIN extents e ON (e.account_fk = t.account_fk) '
             'JOIN partition_domains pd on (pd.partition_fk = dnis.partition_fk) '
             'JOIN domain d on (d.id=pd.domain_fk) '
             'JOIN number_category cat on (dnis.number_category_fk = cat.id) '
             'JOIN data_source ds ON (ds.name = t.ds_name) '
             'JOIN primary_db_server pdbs ON (pdbs.db_server_fk = ds.primary_db_server_fk) '
             'JOIN db_server ON (db_server.id = pdbs.db_server_fk) '
             f'WHERE dnis.name="+19255403841";')
# +19255403841
# 2220000801
#     query = '''
#     SELECT dnis.name number, cat.name category, dnis.grp billing_group, d.name domain_name, t.flags & 1 E164, c_dnis.pd_campaign_fk, c_dnis.dnis_fk, c.name campaign_name
# FROM dnis
# JOIN tenant t ON (t.id = dnis.partition_fk)
# JOIN partition_domains pd on (pd.partition_fk = dnis.partition_fk)
# JOIN domain d on (d.id=pd.domain_fk)
# JOIN number_category cat on (dnis.number_category_fk = cat.id)
# LEFT JOIN pd_campaign_dnis c_dnis on (c_dnis.dnis_fk=dnis.id)
# LEFT JOIN pd_campaign c on (c.id=c_dnis.pd_campaign_fk)
# WHERE dnis.name="2220000801";
# '''

    cursor.execute(query=query)
    for i in cursor.fetchall():
        print(i)

# cursor.close()
conn.close()
