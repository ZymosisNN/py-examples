from argparse import ArgumentParser, FileType


parser = ArgumentParser()

parser.add_argument('-a', nargs='+', choices=['AA', 'BB', 'CC'], metavar='abc')
parser.add_argument('-b', nargs=2, type=int, required=True)
parser.add_argument('-f', type=FileType())
parser.add_argument('pos1')
parser.add_argument('-c', action='store_const', const='PermanentJopa')
parser.add_argument('-z', action='store_false')
parser.add_argument('-X', dest='my_x', default='default value for my_x')
args = parser.parse_args('pos_arg_value -a AA CC -b 1 2 -c -z -f ex_decorator.py'.split())

print(args)
