from threading import Thread
import time
from arikedb import Arikedb, Collection
from redis import Redis

N = 100_000
# HOST = "127.0.0.1"
HOST = "10.0.0.174"
WRITE = 0

data = {
    "adsgcrgcdsgcsdgc"+str(i): i
    for i in range(N)
}
keys = list(data.keys())
data2 = [
    ("adsgcrgcdsgcsdgc"+str(i), i)
    for i in range(N)
]
keys2 = [x[0] for x in data2]


def redis_test(r: Redis):
    t0 = time.time_ns()
    if WRITE:
        r.mset(data)
    else:
        r.mget(keys)
    print(f"Redis time:   {time.time_ns() - t0} ns")


def arikedb_test(coll: Collection):
    t0 = time.time_ns()
    if WRITE:
        coll.ts_variables_set(data2)
    else:
        coll.ts_variables_get(keys2)
    print(f"ArikeDB time: {time.time_ns() - t0} ns")


if __name__ == "__main__":
    arikedb = Arikedb(host=HOST)
    arikedb.connect()

    arikedb.create_collections(["collA"])
    collection = arikedb.collections[0]

    redis = Redis(host=HOST)

    t1 = Thread(target=redis_test, args=(redis,))
    t2 = Thread(target=arikedb_test, args=(collection,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Done")

    arikedb.disconnect()
