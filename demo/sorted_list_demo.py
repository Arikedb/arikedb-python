import random
from arikedb import Arikedb, ValueType


if __name__ == "__main__":
    with Arikedb() as arikedb:

        arikedb.create_collections(["myCollection"])
        my_collection = arikedb.collection("myCollection")

        my_collection.create_sorted_lists([
            ("SortedRandomNumbers", ValueType.Int, 100),
            ("SortedNames", ValueType.String, None)
        ])

        rand_nums_list = my_collection.sorted_list("SortedRandomNumbers")
        names_list = my_collection.sorted_list("SortedNames")

        nums = random.sample(range(15), 15)
        names = [
            "John Doe",
            "Jane Doe",
            "Donald Trump",
            "Elon Musk",
            "Bill Gates",
            "Mark Zuckerberg",
            "Steve Jobs",
            "Tim Cook",
            "Larry Page",
            "Sergey Brin",
            "Larry Ellison",
            "Jeff Bezos",
        ]

        print("==== Random numbers: =====")
        print(nums)

        rand_nums_list.insert([5, 0, 9, -10, -3, -90, 87, 5, -93, 12])
        names_list.insert(names)

        print("\n==== Smallest 5 numbers: =====")
        print(rand_nums_list.smallest(50))

        print("==== Biggest 5 numbers: =====")
        print(rand_nums_list.biggest(50))

        print("\n==== Sorted names: =====")
        for name in names_list.smallest(100)[1]:
            print(name)
