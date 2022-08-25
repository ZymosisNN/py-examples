def f(limit):
    print(f'limit = {limit}')
    for i in range(4):
        print(i)
        if i == limit:
            print('break')
            break
    else:
        print('else')


f(2)
print('-' * 50)
f(10)
