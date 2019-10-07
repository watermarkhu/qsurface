import matplotlib.pyplot as plt


f = open('mop_growth_L32.txt', 'r')

values = []
for line in f:
    values.append(int(line.rstrip("\n")))

b = []
for i, k in enumerate(values[:2000]):
    l = 0 if i == 0 else values[i-1]
    if k - l > 1: b.append(i)

plt.hist(b, bins=20)

plotvals = values[:100]
plt.plot(plotvals)
plt.plot([0, len(plotvals)], [0, len(plotvals)], 'k--')

def get_bucket(size, support, values):
    if support:
        bucket = values[size-1] + size - 2
    else:
        if size < values[0]:
            bucket = size - 1
        else:
            for i, val in enumerate(values):
                if size >= val and size < values[i+1]:
                    bucket = i + size
                    break
    return bucket
