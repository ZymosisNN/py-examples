from distutils.version import LooseVersion
from threading import Semaphore
from typing import Optional, Tuple, Dict, List, Callable

import requests

from chatops_app import storage, rate_limitter
from chatops_app.abstracts import LogMixin, ChatOpsError


class LimitedHttpSession(requests.Session):
    def __init__(self, max_connections: int = 100, rate_limiter: Optional[Callable] = None):
        super().__init__()
        self._semaphore = Semaphore(max_connections)
        self._rate_limiter = rate_limiter

    def request(self, *args, **kwargs) -> requests.Response:
        with self._semaphore:
            if self._rate_limiter:
                self._rate_limiter()
            return super().request(*args, **kwargs)


class SatClientError(ChatOpsError):
    pass


class SatClient(LogMixin):
    LOGIN = '/auth/login/'
    LOGOUT = '/auth/logout/'
    DOMAIN_STATE = '/domains/{}/state'

    def __init__(self, sat_url: str, auth: Tuple[str, str], req_interval: float, max_req_in_process: int):
        """
        @param auth: tuple - ('login', 'password')
        @param sat_url: str -the full url to the sat api (e.g. https://qasat621.scl.five9lab.com:8443/sat-api/v1)
        """
        super().__init__()
        self.url = sat_url
        self.auth = {'userName': auth[0], 'password': auth[1]}
        self.session = LimitedHttpSession(rate_limiter=rate_limitter.RateLimiter(name='SAT', interval=req_interval),
                                          max_connections=max_req_in_process)

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        return False

    def login(self):
        """
        Logs into SAT API with username and password
        """
        response = self.session.post(self.url + self.LOGIN, json=self.auth, verify=False)
        if response.status_code != 204:
            raise SatClientError(f'SAT login failed: {response.text}')

    def logout(self):
        """
        Logs out of SAT API
        """
        response = self.session.post(self.url + self.LOGOUT)
        if response.status_code != 204:
            raise SatClientError(f'SAT logout failed: {response.text}')

    def get_domains_state(self, domain_id: int):
        """
        Get state of domains in SAT
        """
        path = self.url + self.DOMAIN_STATE.format(domain_id)
        response = self.session.get(path)
        return response.json()


def get_latest_sat_url(providers: List[Dict], dc: str) -> str:
    """
    @param providers: list of providers dicts e.g.:
        [
            {
                "name": "Five9-SCL-P2-US8",
                "oid": "148",
                "type1": "providers",
                "version": "12.5.21"
            },
            ...
        ]
    @param dc: str, Data Center
    @return: str, URL of SAT API
    """
    # For Lab providers, convert versions like "1.345" to "9991.345" to be latest comparing to "12.5.21"
    def prepare_version(provider: Dict):
        v = provider['version']
        return LooseVersion('999' + v) if v.startswith('1.') else LooseVersion(v)

    latest_provider = max(providers, key=prepare_version)
    url = storage.get_sat_url(provider_id=int(latest_provider['oid']), dc=dc)
    return url


if __name__ == '__main__':
    test_auth = 'sysop', 'sysop9'
    # test_url = 'https://qasat621.scl.five9lab.com:8443/sat-api/v1'
    test_url = 'https://qasat63.five9lab.com/sat-api/v1'

    with SatClient(auth=test_auth, sat_url=test_url) as sat:
        print(sat.get_domains_state(409))
