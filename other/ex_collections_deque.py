from collections import deque

d = deque(maxlen=5)

for i in range(10):
    d.appendleft(i)
    print(d)

while len(d):
    print(d.popleft())

