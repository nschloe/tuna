import time


def prime(n):
    # compute the n-th prime number, takes longer for larger n
    time.sleep(n)
    return 2


def a(k=1):
    return prime(k)


def b(k=3):
    return prime(k)


def c():
    a(0.1)
    b(0.1)
    time.sleep(1)
    return


if __name__ == "__main__":
    a()
    b()
    c()
