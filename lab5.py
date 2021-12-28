import lab4
import operat

def fastExpMod(message, e, n):
    result = 1
    while e != 0:
        if (e & 1) == 1:
            result = (result * message) % n
            #result = operat.mod(operat.mul(result, message), n)
        e >>= 1
        message = (message * message) % n
        #message = operat.mod(operat.square(message), n)
    return result

# розширений алгоритм Евкліда
def gcd_extended(a, b):
    if a == 0:
        return b, 0, 1

    gcd, x1, y1 = gcd_extended(operat.mod(b, a), a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# вибираємо е - відкритий ключ => 1 < e < fi_n and НДС(e, fi_n) = 1
def gener_e(fi_n):
    e = 4
    for i in range(e, fi_n):
        gcd, _, _ = gcd_extended(i, fi_n)
        if gcd == 1:
            return i


# знаходимо d - закритий ключ => ed = 1 (mod fi_n)
def gener_d(e, fi_n):
    gcd, x, y = gcd_extended(fi_n, e)
    if y < 0:
        y = fi_n + y
    return y

# C = P^e mod n
def encryption(P, e, n):
    return fastExpMod(P, e, n)

# P = C^d mod n
def decryption(C, d, n):
    return fastExpMod(C, d, n)


# генеруємо прості числа p, q
p = lab4.generate_prime_number(512)
q = lab4.generate_prime_number(512)
print(f'p = {p} \nq = {q}')

# n = p * q
n = operat.mul(p, q)

# fi_n = (p - 1) * (q - 1)
fi_n = operat.mul((p - 1), (q - 1))
e = gener_e(fi_n)
d = gener_d(e, fi_n)
print(f'n = {n}, \nfi = {fi_n}, \ne = {e}, \nd = {d}')

P = 936195619503715
print('P = ', P)

cr = encryption(P, e, n)
print(f'encrypted = {cr}')

decr = decryption(cr, d, n)
print(f'decrypted = {decr}')

