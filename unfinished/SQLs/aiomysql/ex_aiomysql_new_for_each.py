import asyncio
import logging
from typing import NamedTuple, List, Tuple, Iterable

import aiomysql
from pymysql.err import OperationalError

from test_dialer.test_dialer_core.abstracts import AbstractVCCDataFetcher


class DBParam(NamedTuple):
    host: str
    port: int
    username: str
    password: str
    db_name: str


def catch_operational_error(result_if_error, logger_name=None):
    def decor(func):
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except OperationalError as exc:
                log = logging.getLogger(logger_name)
                log.error(exc)
                return result_if_error
        return wrapped

    return decor


class AsyncDBDataFetcher(AbstractVCCDataFetcher):
    def __init__(self, param: DBParam, *,
                 private_trunk_pattern=r'%\_trk\_%'):

        self.param = param
        self.private_trunk_pattern = private_trunk_pattern
        self.log = logging.getLogger('AsyncDBDataFetcher')

    async def get_test_anis(self) -> List[str]:
        result = await self.execute_query('SELECT ani FROM test_ani;')
        return [i['ani'] for i in result]

    async def get_private_trunk_dnises(self, dnises: List[str]) -> List:
        dnises_str = ','.join([f'"{d}"' for d in dnises])

        query = (f'SELECT name FROM dnis '
                 f'WHERE grp LIKE "{self.private_trunk_pattern}" '
                 f'AND name in ({dnises_str});')

        results = await self.execute_query(query)
        if not results:
            return []

        return [row['name'] for row in results]

    @catch_operational_error(('', ''), 'AsyncDBDataFetcher')
    async def get_domain_and_campaign(self, dnis: str) -> Tuple[str, str]:
        partition_id, cust_db_host = await self.get_partition_and_cust_db_host(dnis)
        if not partition_id:
            self.log.warning(f'Partition ID and customer DB host are not found in DB for DNIS = "{dnis}"')
            return '', ''

        domain_query = ('SELECT	d.name domain_name '
                        'FROM dnis '
                        'JOIN tenant t ON (t.id = dnis.partition_fk) '
                        'JOIN partition_domains pd on (pd.partition_fk = dnis.partition_fk) '
                        'JOIN domain d on (d.id=pd.domain_fk) '
                        f'WHERE dnis.name="{dnis}";')

        campaign_query = ('SELECT c.name campaign_name '
                          'FROM dnis '
                          'JOIN pd_campaign_dnis c_dnis on (c_dnis.dnis_fk=dnis.id) '
                          'JOIN pd_campaign c on (c.id=c_dnis.pd_campaign_fk) '
                          f'WHERE dnis.name="{dnis}";')

        domain_res, campaign_res = await self.execute_queries((domain_query, campaign_query),
                                                              host=cust_db_host,
                                                              db_name=f'PARTITION_DB_{partition_id}')

        domain = domain_res[0]['domain_name'] if domain_res else ''
        campaign = campaign_res[0]['campaign_name'] if campaign_res else ''
        self.log.info(f'DNIS "{dnis}" assigned to domain "{domain}" and campaign "{campaign}"')

        return domain, campaign

    async def get_partition_and_cust_db_host(self, dnis: str) -> Tuple[str, str]:
        query = ('SELECT '
                 't.id partition_id,'
                 'db_server.host cust_db_host '
                 'FROM dnis '
                 'JOIN tenant t ON (t.id = dnis.partition_fk) '
                 'JOIN data_source ds ON (ds.name = t.ds_name) '
                 'JOIN primary_db_server pdbs ON (pdbs.db_server_fk = ds.primary_db_server_fk) '
                 'JOIN db_server ON (db_server.id = pdbs.db_server_fk) '
                 f'WHERE dnis.name = "{dnis}";')

        result = await self.execute_query(query)
        if not result:
            return '', ''

        return result[0]['partition_id'], result[0]['cust_db_host']

    async def get_domain_dc(self, domain_name: str) -> str:
        last_operation = await self.get_domain_last_operation(domain_name)
        if 'PRIMARY' in last_operation:
            return 'pdc'
        if 'BACKUP' in last_operation:
            return 'bdc'

        self.log.error(f'Cannot parse last operation "{last_operation}"')
        return ''

    @catch_operational_error('', 'AsyncDBDataFetcher')
    async def get_domain_last_operation(self, domain_name: str) -> str:
        query = ('SELECT t.name FROM ha_operations hao '
                 'JOIN ha_operation_domains had ON had.operation_fk = hao.id '
                 'JOIN ha_operation_types t ON (t.ordinal = hao.ha_operation_type_fk) '
                 'JOIN domain d ON (d.id = had.domain_fk) '
                 f'WHERE d.name = "{domain_name}" '
                 'ORDER BY hao.timestamp_ms DESC limit 1;')

        result = await self.execute_query(query)
        return result[0]['name'] if result else ''

    async def execute_query(self, query: str, host='', db_name=''):
        async with self.connect(host, db_name) as connection:
            return await self.execute_via_connection(query, connection)

    async def execute_queries(self, queries: Iterable[str], host='', db_name=''):
        async with self.connect(host, db_name) as connection:
            results = [await self.execute_via_connection(query, connection) for query in queries]
            return results

    def connect(self, host='', db_name=''):
        return aiomysql.connect(host=host or self.param.host,
                                port=self.param.port,
                                user=self.param.username,
                                password=self.param.password,
                                db=db_name or self.param.db_name)

    @staticmethod
    async def execute_via_connection(query, connection):
        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            return await cursor.fetchall()


async def fetch_data(vcc_db: AsyncDBDataFetcher, name: str = '-'):
    log = logging.getLogger(name)
    dnis = '+15995559001'
    domain_name, campaign_name = await vcc_db.get_domain_and_campaign(dnis)
    log.info(f'{domain_name=}  {campaign_name=}')


async def main():
    db_param = DBParam(host='qadb011.scl.five9lab.com', port=3306, username='db59', password='admin', db_name='Five9App')
    vcc_db = AsyncDBDataFetcher(db_param)
    tasks = [asyncio.create_task(fetch_data(vcc_db, f'task-{i}')) for i in range(50)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')

    asyncio.run(main())
