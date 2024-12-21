import sys


def checkBracketsValid(strCheck):
    patternOpen = ('(','[','{')
    patternCloseDict = { ')':'(', ']':'[', '}':'{'}
    brackets = []
    for i in strCheck:
        if i in patternOpen:
            brackets.append(i)
        elif patternCloseDict.get(i, False):
            if brackets != [] and brackets[-1] == patternCloseDict.get(i, False):
                brackets.pop()
            else:
                return False
    if brackets == []:
        return True
    return False


# for i,v in enumerate(sys.argv):
#     if i != 0:
#         print(checkBracketsValid(v))

if __name__ == '__main__':
    from samples import SAMPLES

    for sample in SAMPLES:
        print(sample)
        print(checkBracketsValid(sample))
        print()
