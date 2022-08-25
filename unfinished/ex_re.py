import re


sample = 'begin left  < some bullshit >   right end'

# Using backreference
# after = re.sub(r'(left) +(right)', r'\1_\2', sample)

# Using lookbehind and lookahead
after = re.sub(r'(?<=left).*(?=right)', '_', sample)

print(sample)
print(after)

print('Word boundaries:')
samples = 'parameters -cat', 'parameters -category'
for sample in samples:
    result = re.search(r'.*-cat\b', sample)
    print(result)
