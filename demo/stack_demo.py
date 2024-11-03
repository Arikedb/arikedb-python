from arikedb import Arikedb, ValueType


if __name__ == "__main__":
    with Arikedb() as arikedb:
        # client.authenticate(username="admin", password="admin")

        arikedb.create_collections(["Collection1", "Collection2"])

        collection = arikedb.collections()[0]

        collection.create_stacks([
            ("StackA", ValueType.Float, 6),
        ])
        collection.create_fifos([
            ("FifoA", ValueType.Float, 6),
        ])
        collection.create_sorted_lists([
            ("SortedListA", ValueType.Int, 20),
        ])

        stackA = collection.stacks()[0]
        fifoA = collection.fifos()[0]
        sorted_listA = collection.sorted_lists()[0]
        print(stackA.name)
        print(fifoA.name)
        print(sorted_listA.name)

        x = stackA.put([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        x2 = fifoA.push([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
        # x3 = sorted_listA.insert([4, 6, -2, 10, 5, 9, -4, 6, 8, 23, -123, -2])
        print(x)
        print(x2)
        # print(x3)

        y = stackA.pop(2)
        y2 = fifoA.pull(3)
        big = sorted_listA.biggest(4)
        small = sorted_listA.smallest(40)

        print(y)
        print(y2)

        print(big)
        print(small)
