import argparse
import asyncio
import logging
import sys
import traceback
from datetime import datetime
from getpass import getpass
from time import time
from typing import Tuple, Optional, List

from elasticsearch import AsyncElasticsearch


class BaseEsClient:
    ts_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, *, hosts: List[str], auth: Tuple[str, str], es_index: str, timeout: int):

        self.log = logging.getLogger('BaseEsClient')
        self.hosts = hosts
        self.auth = auth
        self.es_index = es_index
        self._esconn = self._create_connection(timeout)

    def _create_connection(self, timeout):
        return AsyncElasticsearch(hosts=self.hosts, http_auth=self.auth, timeout=timeout,
                                  use_ssl=True, verify_certs=False, ssl_show_warn=False)

    async def find_str_during_period(self, *,
                                     query_string: str,
                                     period: Tuple[Optional[datetime], Optional[datetime]] = (None, None)
                                     ) -> List:

        ts_begin = period[0] or datetime.utcnow()
        ts_end = period[1] or datetime.utcnow()

        gte = ts_begin.strftime(self.ts_format)
        lte = ts_end.strftime(self.ts_format)

        self.log.debug(f'query_string: "{query_string}" gte: {gte} lte: {lte}')

        if ts_begin > ts_end:
            self.log.error('BEGIN timestamp is later than END timestamp!')

        res = await self._esconn.search(
            index=self.es_index,
            ### For elasticsearch lib version >= 7.15:
            # query={
            #     'bool': {
            #         'filter': [
            #             {'term': {'tags': 'siplogs'}},
            #             {'query_string': {'query': query_string}},
            #             {'range': {
            #                 '@timestamp': {'gte': gte, 'lte': lte}
            #             }},
            #         ]
            #     }
            # },
            # size=20
            body={
                'size': 20,
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"tags": "siplogs"}},
                            {"query_string": {"query": query_string}},
                            {"range": {
                                "@timestamp": {"gte": gte, "lte": lte}
                            }},
                        ]
                    }
                },
            }
        )

        hits = res['hits']
        if not hits['total']['value']:
            return []

        return [hit['_source']['message'] for hit in hits['hits']]

    async def close(self):
        self.log.debug('CLOSE ES client')
        await self._esconn.close()


async def main(*, host: List[str], auth: Tuple[str, str], req_timeout: int, req_count: int, query: str, index: str, period: Tuple[str, str]):
    log = logging.getLogger('main')
    es = BaseEsClient(hosts=host, auth=auth, es_index=index, timeout=req_timeout)
    fmt = '%Y-%m-%d %H:%M:%S'
    ts_from = datetime.strptime(period[0], fmt)
    ts_to = datetime.strptime(period[1], fmt)

    durations = []
    for _ in range(req_count):
        start_time = time()
        try:
            res = await es.find_str_during_period(query_string=query, period=(ts_from, ts_to))
            log.info(f'Items found: {len(res)}')
            for i in res:
                log.info(i)
            log.info('')

        except Exception:
            log.error(f'EXCEPTION:\n{traceback.format_exc()}')
            durations.append(f'>{req_timeout}')

        else:
            durations.append(str(round(time() - start_time, 2)))

    log.info(f'Requests durations (sec): {", ".join(durations)}')

    await es.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+20s |  %(message)s')
    log = logging.getLogger()

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='timeout', type=int, default=60)
    parser.add_argument('-n', dest='req_count', type=int, default=1)
    parser.add_argument('-dc', dest='dc', type=str, choices=('us', 'eu', 'lab'), default='lab')
    parser.add_argument('-u', dest='usr', required=True)
    parser.add_argument('-i', dest='idx', choices=('pdc', 'bdc', 'tmp'))

    args = parser.parse_args('-u elasticSuperUser'.split())
    args.pwd = '3!@asticSup3rDuperUser'
    # args.pwd = getpass(f'Enter password: ')

    hosts = {
        'us': ['eccs001.scl.five9.com', 'eccs002.scl.five9.com', 'eccs003.scl.five9.com'],
        'eu': ['esk001.ldn.five9.com'],
        'lab': ['labesd110.infra.five9lab.com'],
    }
    indices = {
        'us': {
            None: 'scl_cluster3:logstash-scl_sip*,atl_cluster2:logstash-atl_sip*',
            'pdc': 'scl_cluster3:logstash-scl_sip*',
            'bdc': 'atl_cluster2:logstash-atl_sip*',
            # 'tmp': 'atl_cluster2:logstash-atl_sip-2021.10.14*',
            'tmp': 'scl_cluster3:logstash-scl_sip-2021.10.14*,scl_cluster3:logstash-scl_sip-2021.10.13*,atl_cluster2:logstash-atl_sip-2021.10.14*,atl_cluster2:logstash-atl_sip-2021.10.13*',
        },
        'eu': {
            None: 'ldn_cluster2:logstash-ldn_sip*,ams_cluster1:logstash-ams_sip*',
            'pdc': 'ldn_cluster2:logstash-ldn_sip*',
            'bdc': 'ams_cluster1:logstash-ams_sip*',
        },
        'lab': {
            None: 'logstash-sclab_sip*',
        },
    }
    periods = {
        # 'us': ('2021-10-12 18:00:00', '2021-10-12 20:00:00'),
        'us': ('2021-10-14 00:00:00', '2021-10-14 23:00:00'),
        'eu': ('2021-10-13 09:00:00', '2021-10-13 11:00:00'),
        'lab': ('2021-10-20 00:00:00', '2021-10-20 23:00:00'),
    }
    queries = {
        'us': '"IN-REQ" AND "INVITE" AND (8554422655 OR 18554422655)',
        'eu': '"IN-REQ" AND "INVITE" AND (1852086785 OR 31852086785)',  # AMS
        'lab': '"IN-REQ" AND "INVITE" AND (9255246171 OR 19255246171)'
    }

    log.info('REQ params:')
    log.info(f'    query: {queries[args.dc]}')
    log.info(f'    number of requests: {args.req_count}')
    log.info(f'    timeout: {args.timeout}')
    log.info(f'    hosts: {hosts[args.dc]}')
    log.info(f'    index: {indices[args.dc][args.idx]}')

    coro = main(host=hosts[args.dc],
                auth=(args.usr, args.pwd),
                req_timeout=args.timeout,
                req_count=args.req_count,
                query=queries[args.dc],
                index=indices[args.dc][args.idx],
                period=periods[args.dc])
    asyncio.run(coro)
