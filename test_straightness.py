
# ar = [(1,1), (1,2), (0,1)]
ar = [(1,0), (0,0)]
# ar = [(0,1), (0,2), (0,3), (1,1), (1,2), (1, 3)]


def ms(m0, r0, m1, r1, L):

    dis = m0 - m1
    distances = [dis, L-abs(dis)]
    abs_distances = [abs(x) for x in distances]

    min_distance = min(abs_distances)
    sign1 = -1 if abs_distances.index(min_distance) == 0 else 1

    if dis != 0:
        sign0 = dis//abs(dis)
        direction = sign0*sign1
    else:
        direction = sign1

    m1s = m0 + direction*min_distance

    lower = min([m0 - r0, m1s - r1])
    upper = max([m0 + r0, m1s + r1])

    mid = (upper+lower)/2%L
    rad = (upper-lower)/2

    return mid, rad

L = 7
S = len(ar)
med = [0, 0]
rad = [0, 0]
for j, a in enumerate(ar, 0):
    if j == 0:
        med = list(a)
        continue

    for i, yx in enumerate(a, 0):

        med[i], rad[i] = ms(med[i], rad[i], yx, 0, L)
        # m, r = med[i], rad[i]
        # baseL, baseH = m - r, m + r
        # bordercross = baseL < 0 or baseH > L
        # newvs_cross = bordercross and yx > baseH%L and yx < baseL%L
        # newvs_noncr = not bordercross and (yx < baseL or yx > baseH)
        # if newvs_noncr or newvs_cross:
        #     LRbound = yx + L if yx < baseL or newvs_cross else yx
        #     HLbound = yx - L if yx > baseH or newvs_cross else yx
        #     newR = [(LRbound - baseL)%L/2, (baseH - HLbound)%L/2]
        #     minR = min(newR)
        #     minM = (LRbound + baseL%L)/2%L if newR.index(minR) == 0 else (baseH%L + HLbound)/2%L
        #     rad[i], med[i] = minR, minM

rad, med
val = S**(1/2)
Rb, Rr = val // 1, val % 1
if Rr == 0:
    R = [(Rb - 1)/2]*2
elif Rr < 0.5:
    R = [(Rb - 1)/2, Rb/2]
else:
    R = [Rb/2]*2

print(med, rad, R)

norm = R[0] + abs(R[1]-(S-1)/2)
straightness = (abs(min(rad)-R[0]) + abs(max(rad)-R[1]))/norm
print(straightness)
