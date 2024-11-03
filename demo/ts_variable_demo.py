from arikedb import Arikedb, ValueType, Event, VarEvent
import time


if __name__ == "__main__":
    with Arikedb() as arikedb:
        # client.authenticate(username="admin", password="admin")

        arikedb.create_collections(["Collection1", "Collection2"])

        collection = arikedb.collections()[0]

        collection.create_ts_variables([
            ("Temperature", ValueType.Float),
            ("Humidity", ValueType.Int),
        ])

        temp, hum = collection.ts_variables()

        temp.set(20.0)
        hum.set(50.0)
        time.sleep(1)

        temp.set(21.0)
        hum.set(51.0)

        temp.set(-34.0)
        hum.set(89.0)
        time.sleep(1)

        temp.set(-12.23)
        hum.set(89.0)
        time.sleep(1)
        print(temp.get())
        print(hum.get())

        collection.variables_subscribe(
            names=["Temperature", "Humidity"],
            events=[VarEvent(Event.OnRise)],
            callback=print,
            callback_kwargs={"sep": "", "end": "   ++++\n"}
        )

        for i in range(10):
            time.sleep(1)

            temp.set(i)
            hum.set(i)

    time.sleep(1)
