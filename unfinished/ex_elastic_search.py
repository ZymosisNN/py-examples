import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, NamedTuple

from elasticsearch import AsyncElasticsearch, SSLError
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
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return AsyncElasticsearch(hosts=self.hosts, basic_auth=self.auth, ssl_context=ctx)

    async def find_str_during_period(self, *,
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

        async def search():
            return await self._esconn.search(
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
            res = await search()
            self.log.info(res)
        except SSLError as ex:
            self.log.exception(ex)
            await self.close()
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

    async def close(self):
        self.log.debug('CLOSE ES client')
        await self._esconn.close()


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

    async def wait_invite(self, *,
                          did: str,
                          from_time: datetime,
                          timeout: int,
                          dc: str
                          ) -> SipEsClientResult:

        if not (invite_log := await self._wait_invite_log(did, from_time, timeout, dc)):
            return SipEsClientResult(invite_found=False)

        self._log_found_invite(invite_log)
        timestamp = self._fetch_timestamp_from_invite(invite_log)
        carrier_name = self._fetch_carrier_from_invite(invite_log)

        return SipEsClientResult(invite_found=True, invite_timestamp=timestamp, carrier_name=carrier_name)

    async def _wait_invite_log(self, did: str, from_time: datetime, timeout: int, dc: str) -> str:
        wait_end_time = from_time + timedelta(
            seconds=max(timeout, self.es_refresh_interval) + self.polling_interval)
        first_attempt = True

        if datetime.utcnow() < wait_end_time:
            seconds_to_wait = (wait_end_time - datetime.utcnow()).seconds
            self.log.debug(f'Wait {seconds_to_wait} seconds for invite "{did}" log in "{dc}" DC')
        else:
            self.log.debug(f'Check once for invite "{did}" log in "{dc}" DC')

        while datetime.utcnow() <= wait_end_time or first_attempt:
            first_attempt = False
            query = f'"IN-REQ" AND "INVITE" AND "{did}"'
            if res := await self.find_str_during_period(query_string=query, period=(from_time, None), dc=dc):
                if len(res) > 1:
                    self.log.warning(f'Expected 1 invite, got {len(res)}, using the first')
                return res[0]

            await asyncio.sleep(self.polling_interval)

        self.log.debug(f'Invite from "{did}" not found')
        return ''

    def _fetch_timestamp_from_invite(self, log_txt: str) -> Optional[datetime]:
        if match := self.INVITE_TIMESTAMP_PATTERN.search(log_txt):
            ts_str = str(datetime.utcnow().year) + match.group('ts')  # Add year because invite has not
            ts = datetime.strptime(ts_str, self.INVITE_TIMESTAMP_FMT)
            return ts.astimezone(self.LOCAL_ZONE)
        else:
            self.log.error(f'Cannot fetch timestamp from log:\n{log_txt}')

    def _fetch_carrier_from_invite(self, log_txt: str) -> str:
        for pattern in self.CARRIER_NAME_PATTERNS:
            if match := pattern.search(log_txt):
                carrier_name = match.group("carrier_name")
                self.log.debug(f'Carrier name: "{carrier_name}"')
                return carrier_name

        self.log.debug('Carrier name is not found')
        return ''

    def _log_found_invite(self, log_txt: str):
        self.log.debug('-' * 50)
        for i in log_txt.split(self.DELIMITER):
            self.log.debug(i)


async def self_test():
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
    await es.find_str_during_period(query_string='5995559001', period=(ts_begin, None), dc='')

    # invite_res = await es.wait_invite(did='+19255246171', from_time=datetime.utcnow(), timeout=4, dc='')
    # es.log.critical(f'invite_res = {invite_res}')

    await es.close()


if __name__ == '__main__':
    import sys
    # from elastic_transport import debug_logging

    fmt = '%(asctime)-15s  |%(levelname)+8s| %(name)+35s |  %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=fmt, stream=sys.stdout)

    # debug_logging()

    asyncio.run(self_test())
