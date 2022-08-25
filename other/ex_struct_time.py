from datetime import datetime


####################################################################################
# strftime
# format to string
####################################################################################
time_format = 'Year:%Y Month:%m Day:%d Hour:%H Minute:%M Second:%S'
str_time = datetime.now()
print('Now:', str_time)
time_string = str_time.strftime(time_format)
print('Formatted time:', time_string)
print('-' * 100)

####################################################################################
# strptime
# parse from string
####################################################################################
time_format = '%Y-%m-%d %H:%M:%S'
time_string = '2019-09-17 22:42:10'
str_time = datetime.strptime(time_string, time_format)
print(str_time, type(str_time))
print(str_time.year)
print(str_time.month)
print(str_time.day)
print(str_time.hour)
print(str_time.minute)
print(str_time.second)
