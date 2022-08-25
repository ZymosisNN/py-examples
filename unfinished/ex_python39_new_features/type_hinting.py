def func(d: dict[int, str]):
    for k, v in d.items():
        print(f'{str(k).rjust(5)} - {v}')


dd = {1: 'one', 20: 'twenty', 333: 'three three three'}
func(dd)
