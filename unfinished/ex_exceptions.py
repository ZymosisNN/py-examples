import traceback
# a()

try:
    a()

except NameError:
    print(traceback.format_exc())
