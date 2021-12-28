import numpy as np

def add(n1, n2):
    n1 = list(map(int, str(n1)))
    n1.reverse()
    n2 = list(map(int, str(n2)))
    n2.reverse()

    res_size = max(len(n1), len(n2)) + 1

    while len(n1) < res_size:
        n1.append(0)
    while len(n2) < res_size:
        n2.append(0)

    res = []
    perenos = 0
    for i in range(res_size):
            x = n1[i] + n2[i] + perenos
            if x >= 10:
                res.append(x % 10)
                perenos = 1
            else:
                res.append(x)
                perenos = 0

    res.reverse()
    if res[0] == 0:
        res.pop(0)

    res = int("".join(map(str, res)))

    return res

def mul(n1, n2):
    n1 = list(map(int, str(n1)))
    n2 = list(map(int, str(n2)))

    res_size = len(n1) + len(n2) + 1
    ans = np.zeros(res_size)
    for i in range(len(n1)):
        for j in range(len(n2)):
            ans[i + j] += int(n1[len(n1) - i - 1] * n2[len(n2) - j - 1])
            ans[i + j + 1] += int(ans[i + j] / 10)
            ans[i + j] %= 10

    res = np.flip(ans)
    if res[0] == 0:
        res = np.delete(res, 0)
    res = res.tolist()
    res = list(map(int, res))
    res = int("".join(map(str, res)))

    return res

def square(n):
    return mul(n, n)

def mod(n, a):
    n = list(map(int, str(n)))
    res = 0

    for i in range(0, len(n)):
        res = (res * 10 + int(n[i])) % a

    return res
