import random
from arikedb import Arikedb, ValueType, Event, VarEvent, Collection
import time


if __name__ == "__main__":
    with Arikedb(host="localhost", username="ale", password="ale") as arikedb:

        # arikedb.create_collections(["Collection1", "Collection2"])

        coll1 = arikedb.collection("jsColl1")
        v1 = coll1.ts_variable("var1")
        v2 = coll1.ts_variable("var2")

        v1.set(10)
        v2.set("Alejandrodfgdfg")

        t0 = time.time()
        # collection1.create_ts_variables(
        #     [(f"var{i}", ValueType.Float) for i in range(100)]
        # )

        # collection1.ts_variables_set(
        #     [(f"var{i}", random.random() * 10) for i in range(100)]
        # )

        # for name, timestamp, value in collection1.ts_variables_get([f"var{i}" for i in range(100)]):
        #     print(name, timestamp, value)

        # print(f"Time: {time.time() - t0}")

        # collection1.variables_subscribe(
        #     names=[f"var{i}" for i in range(3)],
        #     events=[
        #         VarEvent(Event.OnRise),
        #         VarEvent(Event.OnUnderLowLimit, low_limit=50.0),
        #     ],
        #     callback=print,
        #     callback_args=(" End Text",),
        #     callback_kwargs={"end": "\n\n"}
        # )

        # for i in range(100):
        #     collection1.ts_variables_set([(f"var{i}", random.random() * 100) for i in range(3)])
        #     time.sleep(1)
