import csv
import dataclasses
import hashlib as hs
import multiprocessing
import random
import secrets
import string
import time
import timeit


@dataclasses.dataclass
class ResultRow:
    length: int
    tries: int
    alg_results: dict[str, 'AlgResult']


@dataclasses.dataclass
class AlgResult:
    time: float
    collisions: float


def main():
    before = time.time()
    lengths = [1, 10, 100, 1000, 10000, 100000]
    with multiprocessing.Pool(len(lengths)) as pool:
        results = pool.map(experiment, lengths)

    # for length in :
    #     results.append(experiment(length))
    after = time.time()
    print(f"Czas eksperymentu (w sekundach): {after - before}")

    with open("results.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(['string_length', 'number_of_tries', 'hash_name', 'avg_time', 'collisions_ratio'])
        for result in results:
            for alg_name, res in result.alg_results.items():
                writer.writerow([result.length, result.tries, alg_name, f'{res.time:,}' , res.collisions])


def experiment(length: int) -> ResultRow:
    functions = [md5, sha256, sha3, sha1, blake2s]
    tries = min(10000, len(string.printable) ** length)
    results = {}

    cols = {f.__name__: set() for f in functions}
    times = {f.__name__: [] for f in functions}
    for s in random_strings(length, tries):
        s = s.encode('utf-8')
        for f in functions:
            times[f.__name__].append(
                timeit.timeit(lambda: f(s), number=1)
            )
            cols[f.__name__].add(f(s))
    for f in functions:
        collisions = tries - len(cols[f.__name__])
        avg_time = sum(times[f.__name__]) / len(times[f.__name__])
        results[f.__name__] = AlgResult(avg_time, collisions)
    return ResultRow(length, tries, results)


def generate_random_string(length):
    alphabet = string.printable
    while True:
        random_string = ''.join(secrets.choice(alphabet) for _ in range(length))
        if random_string not in used_strings:
            used_strings.add(random_string)
            return random_string
used_strings = set()


def random_strings(length, tries):
    for _ in range(tries):
        yield generate_random_string(length)


def md5(s: bytes) -> str:
    return hs.md5(s).hexdigest()


def sha256(s: bytes) -> str:
    return hs.sha256(s).hexdigest()


def sha3(s: bytes) -> str:
    return hs.sha3_256(s).hexdigest()


def sha1(s: bytes) -> str:
    return hs.sha1(s).hexdigest()


def blake2s(s: bytes) -> str:
    return hs.blake2s(s).hexdigest()


if __name__ == '__main__':
    main()
