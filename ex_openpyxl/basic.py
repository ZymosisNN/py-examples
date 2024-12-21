import pandas
from pathlib import Path


df = pandas.read_excel(Path('nf_ips.xlsx'))

res = df[df['nf_name'] == 'AMF']['ip']

print(type(df))
print(df)


print(type(res))
print(res)


# for nf_cell, ip_cell in ws['a1': 'b5']:
#     print(nf_cell.value)
#     print(ip_cell.value)
#     print('')
#
#
