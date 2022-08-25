import requests


session = requests.Session()

result = session.get('https://qaus01.five9lab.com/login/')
print(result.content)

print('-' * 100)

result = session.get('https://qaus01.five9lab.com/settings/')
print(result.content)

