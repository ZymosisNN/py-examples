import requests

jmx_user = 'sysop'
jmx_password = 'sysop9'

cores = [811, 812]
# twiddle_url = 'http://qacore{}.nn.five9lab.com:8080/twiddle'
# twiddle_url = 'http://qacore{}.scl.five9lab.com:8080/twiddle'

# twiddle_url = 'http://10.27.72.18:8080/twiddle'

twiddle_url = 'https://vcccore01.grmm.lx-draskin5.five9.com:8443/twiddle'

# cmd = 'query "*:domainName={},service=com.five9.cc.spi.CallCenterService,*"'.format(dom)
# cmd = 'query "*:domainName=mm_*,service=com.five9.cc.spi.CallCenterService,*"'
cmd = 'invoke five9.ha:service=HaManager startLocalDomainMigrationTAG 111,222 11 22 1 3 3'

# cmd = 'invoke  five9.ha:service=HaManager performDomainHaOperationTAG %s %s %s' % ('11,22', 'DOMAIN_FAILOVER_TO_BACKUP', 10)
# cmd = 'invoke  five9.ha:service=HaManager performDomainHaOperationTAG 11,22 DOMAIN_FAILOVER_TO_BACKUP 10'

print('')
# for core in cores:
#     response = requests.post(twiddle_url.format(core), data=cmd, auth=(jmx_user, jmx_password), timeout=10)
#     if response.ok:
#         print 'Deployed "mm_*" domains on core {}:'.format(core)
#         print response.text.strip()
#     else:
#         print 'No deployed "mm_*" domains on core {}'.format(core)
#     print ''

response = requests.post(twiddle_url, data=cmd, auth=(jmx_user, jmx_password), timeout=10, verify=False)

print(response.text.strip())

# if response.ok:
#     print('Deployed "mm_*" domains on core 621:')
#     print(response.text.strip())
# else:
#     print('No deployed "mm_*" domains on core 621')
