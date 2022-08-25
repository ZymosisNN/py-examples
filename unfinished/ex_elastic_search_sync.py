import logging
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, NamedTuple

from elasticsearch import Elasticsearch, SSLError
from tzlocal import get_localzone

import ssl


class BaseEsClient:
    ts_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, *,
                 hosts: List[str],
                 auth: Tuple[str, str],
                 es_index_common: str,
                 es_index_pdc: str,
                 es_index_bdc: str):

        self.log = logging.getLogger('BaseEsClient')
        self.hosts = hosts
        self.auth = auth
        self.es_indices = {
            '': es_index_common,
            'pdc': es_index_pdc,
            'bdc': es_index_bdc,
        }

        self._esconn = self._create_connection()

    def _create_connection(self):
        # TODO: check that timeout=300 is not really needed anymore
        # ctx = ssl.create_default_context()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # c = ctx.get_ciphers()
        # self.log.info(c)

        return Elasticsearch(hosts=self.hosts, basic_auth=self.auth, ssl_version=ssl.TLSVersion.TLSv1_3)
        # return AsyncElasticsearch(hosts=self.hosts, basic_auth=self.auth, ssl_show_warn=True, ssl_context=ctx)
        # return AsyncElasticsearch(hosts=self.hosts, basic_auth=self.auth, verify_certs=False, ssl_show_warn=False, ssl_context=ctx)

    def find_str_during_period(self, *,
                               query_string: str,
                               period: Tuple[Optional[datetime], Optional[datetime]] = (None, None),
                               dc: str
                               ) -> List:

        ts_begin = period[0] or datetime.utcnow()
        ts_end = period[1] or datetime.utcnow()

        gte = ts_begin.strftime(self.ts_format)
        lte = ts_end.strftime(self.ts_format)

        self.log.debug(f'query_string: "{query_string}" gte: {gte} lte: {lte}')

        if ts_begin > ts_end:
            self.log.error('BEGIN timestamp is later than END timestamp!')

        def search():
            return self._esconn.search(
                index=self.get_es_index_for_dc(dc),
                size=20,
                query={
                    "bool": {
                        "filter": [
                            {"term": {"tags": "siplogs"}},
                            {"query_string": {"query": query_string}},
                            {"range": {
                                "@timestamp": {"gte": gte, "lte": lte}
                            }},
                        ]
                    }
                }
            )

        try:
            res = search()
        except SSLError as ex:
            self.log.exception(ex)
            self.close()
            raise

        hits = res['hits']
        if not hits['total']['value']:
            return []

        return [hit['_source']['message'] for hit in hits['hits']]

    def get_es_index_for_dc(self, dc: str):
        try:
            return self.es_indices[dc]
        except KeyError as exc:
            raise Exception(f'Unsupported DC "{dc}"') from exc

    def close(self):
        self.log.debug('CLOSE ES client')
        self._esconn.close()


class SipEsClientResult(NamedTuple):
    invite_found: bool
    invite_timestamp: datetime = None
    carrier_name: str = ''


class SipEsClient(BaseEsClient):
    DELIMITER = '#015#012'
    INVITE_TIMESTAMP_PATTERN = re.compile(r'(?P<ts>\w{3} +\d{1,2} +\d{2}:\d{2}:\d{2})')
    INVITE_TIMESTAMP_FMT = '%Y%b %d %H:%M:%S'
    CARRIER_NAME_PATTERNS = (re.compile(rf'X-Carrier-Name: (?P<carrier_name>\S+?){DELIMITER}'),
                             re.compile(r';otg=(?P<carrier_name>\S+?)>;'))
    LOCAL_ZONE = get_localzone()

    def __init__(self, *,
                 hosts: List[str],
                 auth: Tuple[str, str],
                 es_index_common: str,
                 es_index_pdc: str,
                 es_index_bdc: str,
                 es_refresh_interval: int,
                 polling_interval=3):

        super().__init__(hosts=hosts,
                         auth=auth,
                         es_index_common=es_index_common,
                         es_index_pdc=es_index_pdc,
                         es_index_bdc=es_index_bdc)

        self.log = logging.getLogger('SipEsClient')
        self.es_refresh_interval = es_refresh_interval
        self.polling_interval = polling_interval
        self.log.info(f'Created (hosts: {hosts}, polling_interval: {polling_interval} sec)')


def self_test():
    es = SipEsClient(
        hosts=['https://labesd110.infra.five9lab.com:9200'],
        # hosts=['https://labesk101.infra.five9lab.com:9200'],
        auth=('elasticSuperUser', '3!@asticSup3rDuperUser'),
        es_index_common="logstash-*",
        es_index_pdc='FAKE',
        es_index_bdc='FAKE',
        es_refresh_interval=5,
        polling_interval=3
    )

    time_format = '%Y-%m-%d %H:%M:%S'
    time_string = '2020-08-18 01:02:03'
    ts_begin = datetime.strptime(time_string, time_format)
    es.find_str_during_period(query_string='5995559001', period=(ts_begin, None), dc='')

    # invite_res = await es.wait_invite(did='+19255246171', from_time=datetime.utcnow(), timeout=4, dc='')
    # es.log.critical(f'invite_res = {invite_res}')

    es.close()


if __name__ == '__main__':
    import sys
    # from elastic_transport import debug_logging

    fmt = '%(asctime)-15s  |%(levelname)+8s| %(name)+35s |  %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=fmt, stream=sys.stdout)

    # debug_logging()

    self_test()
