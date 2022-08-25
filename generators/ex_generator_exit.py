def my_gen():
    try:
        for i in range(4):
            yield i
    except GeneratorExit:
        print('GeneratorExit raised')
        raise

    print('my_gen DONE')


def main():
    gen = my_gen()
    for n, i in enumerate(gen):
        print(i)
        if n > 1:
            gen.close()


if __name__ == '__main__':
    main()
