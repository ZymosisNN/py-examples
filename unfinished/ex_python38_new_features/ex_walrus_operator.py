import re

data = 'Preved, debil!'
pattern = r' (.+)!'

# Usual "if"
if m := re.search(pattern, data):
    print(m.group(1))

# or this
name = match.group(1) if (match := re.search(pattern, data)) else None
print(name)
