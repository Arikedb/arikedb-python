from arikedb import Arikedb, ValueType, Collection
import time


if __name__ == "__main__":
    with Arikedb(username="ale", password="qwe") as arikedb:
        arikedb.create_collections(["Collection1", "Collection2"])
        collA = Collection("CollectionA", arikedb)

        for coll in arikedb.collections:
            print(coll.name)
