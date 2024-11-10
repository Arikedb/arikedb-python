from arikedb import Arikedb, ValueType


if __name__ == "__main__":
    with Arikedb() as arikedb:

        arikedb.create_collections(["myCollection"])
        my_collection = arikedb.collection("myCollection")

        my_collection.create_fifos([
            ("Fifo1", ValueType.Bool, 5),
        ])

        fifo1 = my_collection.fifo("Fifo1")

        fifo1.push([True, False, True])
        fifo1.push([False, False])

        print(fifo1.pull(3))

        print(fifo1.pull(20))
