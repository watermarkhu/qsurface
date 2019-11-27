
ar = [(1,1), (1,2), (0,1)]
ar = [(1,1), (1,2), (2,2), (2,3), (3,3)]
# ar = [(1,1), (1, 2), (1,3), (0,2), (2,2)]
# ar = [(0,3), (0,2), (0,1), (0,0), (0,4)]

L = 5

med = [0, 0]
rad = [0, 0]
S = 0
for j, a in enumerate(ar, 0):
    S += 1
    for i, yx in enumerate(a,0):
        if S == 1:
            med[i] = yx
            continue
        baseL = (med[i] - rad[i]) % L
        baseH = (med[i] + rad[i]) % L
        distances = [
            abs(baseL - yx),
            abs(baseH - yx),
            abs((baseL - yx - L)),
            abs((baseH - yx - L)),
        ]
        type = [k for k, a in enumerate(distances) if a == min(distances)]
        if (0 in type and yx < baseL) or (1 in type and yx > baseH):
            med[i] = (med[i]*(rad[i]*2 + 1) + yx)/(rad[i]*2+2)
            rad[i] += .5
        elif (2 in type and yx > baseL) or (3 in type and yx < baseH):
            med[i] = (med[i]*(rad[i]*2 + 1) + yx + L)/(rad[i]*2+2)%L
            rad[i] += .5


num = 2 * ((rad[0]**2 + rad[1]**2)/((len(ar)-1)/2)**2 - .5)
num

num = 0.5
bucket = 4
-(-bucket*num*0.5//1)
