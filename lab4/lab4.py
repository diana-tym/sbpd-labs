from random import randint, getrandbits
import operat

# тест Міллера-Рабіна
def is_prime(n, k):
    if n % 2 == 0:
        return False

    # n - 1 = 2^s * t
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2

    for _ in range(k):
        a = randint(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = operat.mod(operat.square(x), n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

# генерування випадкового числа заданої довжини
def generate_prime_candidate(n_bits):
    p = getrandbits(n_bits)
    p |= (1 << n_bits - 1) | 1   # встановлення першого та останнього бітів в одиницю
    return p

def generate_prime_number(n_bits):
    p = 4
    while not is_prime(p, 10):
        p = generate_prime_candidate(n_bits)
    return p

#p1 = generate_prime_candidate(1024)
#p2 = generate_prime_candidate(1024)

#print(f'p1 = {p1} \np2 = {p2}')