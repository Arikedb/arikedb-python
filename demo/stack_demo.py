from arikedb import Arikedb, ValueType


if __name__ == "__main__":
    with Arikedb(username="ale", password="ale") as arikedb:

        arikedb.create_collections(["myCollection", "myCollection2"])
        my_collection = arikedb.collection("myCollection")

        my_collection.create_stacks([
            ("StackA", ValueType.Float, 5),
        ])

        stack_a = my_collection.stack("StackA")

        stack_a.put([1.0, 2.3])
        stack_a.put([3.1, 4.3, 5.6])

        print(stack_a.pop(3))

        print(stack_a.pop())
