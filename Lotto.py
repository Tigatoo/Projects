#!/usr/bin/env python3
from itertools import product

total_count = 0
prime_count = 0

prime = [2,3,5,7,11,13,17,19,23,29,31]

visited = []

interval = range(1,12)
cartesian = [range(1,36), range(1,35), range(1,34), range(1,33), range(1,32)]
cartesian = [interval, interval, interval, interval, interval]
for i1, i2, i3, i4, i5 in product(*cartesian):
    combi = set({i1, i2, i3, i4, i5})

    if (combi in visited) or len(combi) != 5:
        continue

    visited.append(combi)
    total_count += 1

    if max(combi) in prime:
        prime_count += 1

print('total count: ', total_count)
print('prime count: ', prime_count)
print('percentage: ', prime_count/total_count)
