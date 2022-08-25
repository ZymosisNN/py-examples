import ldap
import logging
import sys


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')

log = logging.getLogger(__name__)

server = 'ldap://ipa002.infra.five9lab.com:636'

ad = ldap.initialize(server)
log.info(ad)

ldap.set_option()
ldap.OPT_X_TLS_REQUIRE_CERT

# LDAPSearch("ou=Organizational Units,dc=five9,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

user = "uid=kgordeev,ou=Organizational Units,dc=five9,dc=com"

res = ad.simple_bind_s(user, 'Autumn2020')
log.info(res)

