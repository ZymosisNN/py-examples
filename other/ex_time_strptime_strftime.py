"""
https://docs.python.org/3/library/time.html
"""
import time

txt_to_parse = '2019-10-11 15:16:17'

fmt_in = '%Y-%m-%d %H:%M:%S'
str_time = time.strptime(txt_to_parse, fmt_in)
print(str_time)

fmt_out = '%j %b %y -- %I%p : %M : %S -- %a %A'
converted_time = time.strftime(fmt_out, str_time)
print(converted_time)
