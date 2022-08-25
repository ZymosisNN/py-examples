from collections import namedtuple


CountryData = namedtuple('CountryData', 'country code international_prefix')

countries = [
    CountryData('north', 1, '011'),
    CountryData('uk', 44, '00'),
]


for country in countries:
    print(country.country, country.code, country.international_prefix)
