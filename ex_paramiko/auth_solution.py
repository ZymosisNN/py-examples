import os
import sys

import paramiko
from paramiko import DSSKey, RSAKey, ECDSAKey, Ed25519Key
from paramiko.agent import Agent
from paramiko.auth_strategy import (
    AuthStrategy, InMemoryPrivateKey, OnDiskPrivateKey, NoneAuth, Password,
)


class Baton(object):
    allowed_types = ()
    hostname = None
    username = None
    password = None


class CustomNoneAuth(NoneAuth):

    def __init__(self, username, baton):
        super().__init__(username)
        self.baton = baton

    def authenticate(self, transport):
        try:
            return super().authenticate(transport)
        except paramiko.BadAuthenticationType as e:
            self.baton.allowed_types = e.allowed_types
            raise


class CustomAuthStrategy(AuthStrategy):

    def __init__(self, baton, ssh_config):
        self.baton = baton
        super().__init__(ssh_config)

    def get_sources(self):
        baton = self.baton
        yield CustomNoneAuth(baton.username, baton)
        for type_ in baton.allowed_types:
            if type_ == 'publickey':
                yield from self._agent_keys()
                yield from self._home_keys()
                continue
            if type_ == 'password':
                yield Password(baton.username, lambda: baton.password)
                continue

    def _agent_keys(self):
        username = self.baton.username
        agent = Agent()
        try:
            for pkey in agent.get_keys():
                yield InMemoryPrivateKey(username, pkey)
        finally:
            agent.close()

    def _home_keys(self):
        username = self.baton.username
        dir_ = os.path.expanduser('~/.ssh')
        for klass, filename in (
                (Ed25519Key, 'id_ed25519'),
                (ECDSAKey, 'id_ecdsa'),
                (RSAKey, 'id_rsa'),
                (DSSKey, 'id_dsa'),
        ):
            path = os.path.join(dir_, filename)
            try:
                pkey = klass.from_private_key_file(path)
            except:
                continue
            else:
                yield OnDiskPrivateKey(username, 'implicit-home', path, pkey)


def main():
    baton = Baton()
    baton.hostname, baton.username, baton.password = sys.argv[1:]
    paramiko.util.log_to_file('/dev/stderr')
    config = paramiko.SSHConfig()
    auth_strategy = CustomAuthStrategy(baton, config)
    with paramiko.SSHClient() as cli:
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        cli.connect(baton.hostname, auth_strategy=auth_strategy)
        print(cli.get_transport())


if __name__ == '__main__':
    main()
