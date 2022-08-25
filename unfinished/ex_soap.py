from suds.client import Client
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

wsdl_five9 = 'https://qawebapi01.five9lab.com/wsadmin/v12/AdminWebService?wsdl&user=ko'

client = Client(wsdl_five9, username='ko', password='kgPass12#')


result = client.service.modifyUser(userGeneralInfo={'userName': 'ko_user_01',
                                                    'password': 'kgPass12#2',
                                                    'canChangePassword': True,
                                                    'mustChangePassword': False})

print(result[0])
