import configparser


config = configparser.ConfigParser()
config.read('ex_config.cfg')

for i in config.items():
    print(i)
