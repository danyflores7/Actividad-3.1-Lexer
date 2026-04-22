# Sieve of Eratosthenes
def sieve_of_eratosthenes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [num for num, prime in enumerate(is_prime) if prime]

def main():
    limit = 100
    primes = sieve_of_eratosthenes(limit)
    print(f"Primes up to {limit}: {primes}")
    print(f"Count: {len(primes)}")

if __name__ == "__main__":
    main()
