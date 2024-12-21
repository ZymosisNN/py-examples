import re
from uuid import UUID


patt = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}')
uu = '14401440-0000-0000-0000-000000000c1f'

print(patt.match(uu))
