# ArikeDB Python Library

Welcome to the ArikeDB Python library! This library provides an interface to interact with the Arike Database,
an advanced real-time database solution. This documentation will guide you through the process of setting up and using the library effectively.

## Installation

To use the ArikeDB python library, install it using pip:

```bash
~$ pip install arikedb
```

## Connecting to ArikeDB

To connect to an ArikeDB server instance, bring `Arikedb` class into scope and create an instance.
The new instance will allow you connect and disconnect using the methods with those names or using it as
a context manager:

```python
from arikedb import Arikedb, Collection, ValueType
```

### Using *connect* and *disconnect* methods
```python
client = Arikedb(host="127.0.0.1")
client.connect()
# ... Here you can use the client instance
#     and any other object to read and write
#     in the database
client.disconnect()
```

### Using client as a context manager
When using the client as a context manager, it will call *connect* and *disconnect* methods under the hood
```python
with Arikedb(host="127.0.0.1") as client:
    # ... Here you can use the client instance
    #     and any other object to read and write
    #     in the database
```

### Possible connection parameters with their default values
```python
host: str = "127.0.0.1"
port: int = 6923
username: Optional[str] = None
password: Optional[str] = None
use_ssl_tls: bool = False
ca_path: Optional[str] = None
cert_path: Optional[str] = None
key_path: Optional[str] = None
```

## Collections

ArikeDB organizes data into collections. Each collection has a name and can contain some data structures

### Creating collections
```python
client.create_collections(names=["collection1", "collection2", "collection3"])
```

### Deleting Collections

```python
client.delete_collections(names=["collection3"])
```

### Listing Collections

```python
for collection in client.collections():
    print(collection.name)

# Also can take a match pattern

for collection in client.collections("*1"):
    print(collection.name)
```
Expected Output:
```
collection1
collection2
collection1
```

## Data structures
Currently arikedb collections support next data structures
 - Time Series Variable
 - Stack
 - Fifo
 - Sorted List

### Time Series Variable
First, let's create some variables in the collection **collection1**

To get the **collection1** instance we have two options
 - Get the collection from the server (return None if it does not exist)

```python
collection1 = client.collection("collection1")
```
 - Just create an instance with that name giving it the client reference

```python
# Assuming there is a `collection1`
collection1 = Collection("collection1", client)
```

Once we have the collection we can create some time series variables. These variables allows us to store real time typed values with high availability over the network.

```python
collection1.create_ts_variables(
    [
        ("var1", ValueType.Int),
        ("var2", ValueType.Float),
        ("var3", ValueType.String),
        ("var4", ValueType.Bool),
    ]
)
```

Now let's list the created variables

```python
for var in collection1.ts_variables():  # Also can take a pattern like `var*` etc
    print(f"{var.name}: type: {var.vtype}")
```
Expected Output:
```
var1: type: ValueType.Int
var2: type: ValueType.Float
var3: type: ValueType.String
var4: type: ValueType.Bool
```

Now we can remove some variables

```python
collection1.delete_ts_variables(["ts_var3", "ts_var4"])
# And list them again
for var in collection1.ts_variables:
    print(f"{var.name}: type: {var.vtype}")
```
Expected Output:
```
var1: type: ValueType.Int
var2: type: ValueType.Float
```

To set and get the value of one variable we can use the TsVariable instance. Similar to the collections, we have two options:

 - List the collection variables and get the one with the required name
```python
var1 = [v for v in collection1.ts_variables if v.name == "var1"][0]
```
 - Or create the instance passing it the actual type and the collection reference
```python
var1 = TsVariable("var1", ValueType.Int, collection1)
```

Now, we can set and get the variable value

```python
# To set the value we can optionally pass the timestamp in ns, or not to use the current timestamp
var1.set(34, time.time_ns())
var1.set(-98)

# The get method returns a tuple with (var name, timestamp in ns, value)
print(var1.get())
```
Expected Output:
```
('var1', 1731125259366534807, -98)
```

When we need to set and get many variables at the same time is much more efficient to make a simple api call by using the collection instance:

```python
collection1.create_ts_variables([(f"float_var{i}", ValueType.Float) for i in range(100)])

collection1.ts_variables_set([(f"float_var{i}", random.random() * 10) for i in range(100)])

for name, timestamp, value in collection1.ts_variables_get([f"var{i}" for i in range(100)]):
    print(name, timestamp, value)
```
Expected Output:
```
var0 1731125750334694996 9.749274644422355
var1 1731125750334711871 1.276401297758929
var2 1731125750334716141 3.772412342332755
var3 1731125750334719579 3.4859678066917956
var4 1731125750334725412 2.456353749978517
var5 1731125750334729110 7.295265352772196
var6 1731125750334733225 0.10315743003679989
var7 1731125750334736923 1.0277357954831046
var8 1731125750334741141 5.681074316239375

........

```

One of the best features of Time Series Variables are Event Subscriptions. You can subscribe multiple variables over multiple events. Available events are under enumerator **Event**:

```python
OnSet
OnChange
OnKeep
OnRise
OnFall
OnValueReachVal
OnValueEqVal
OnValueLeaveVal
OnValueDiffVal
OnCrossHighLimit
OnCrossLowLimit
OnOverHighLimit
OnUnderLowLimit
OnValueReachRange
OnValueInRange
OnValueLeaveRange
OnValueOutRange
```

Let's make an example:

```python
collection1.variables_subscribe(
    names=[f"var{i}" for i in range(3)],
    events=[
        VarEvent(Event.OnRise),
        VarEvent(Event.OnUnderLowLimit, low_limit=50.0),
    ],
    callback=print,
    callback_args=(" End Text",),
    callback_kwargs={"end": "\n\n"}
)

for i in range(100):
    collection1.ts_variables_set([(f"var{i}", random.random() * 100) for i in range(3)])
    time.sleep(1)
```
Expected Output:
```
........

('var0', 1731127595069756690, 3.5209475578207194)  End Text

('var1', 1731127595069785440, 82.59999895955806)  End Text

('var2', 1731127595069791221, 44.76482124800996)  End Text

('var0', 1731127596081695621, 47.739687942724416)  End Text

('var1', 1731127596081708225, 93.65447201838202)  End Text

('var2', 1731127596081712495, 1.69536935524075)  End Text

('var0', 1731127597095884839, 98.58611346783405)  End Text

('var1', 1731127597095896766, 97.79476614542591)  End Text

('var2', 1731127597095900516, 77.31499239759563)  End Text

('var0', 1731127598173467368, 99.8804795300193)  End Text

('var2', 1731127598173484712, 46.714103742400845)  End Text

........

```

### Sorted List

Sorted lists are arrays of typed values which are automatically sorted when they are inserted 

```python
collection1.create_sorted_lists([
    ("SortedRandomNumbers", ValueType.Int, 20),  # 20 will be the max size of the list
    ("SortedNames", ValueType.String, None)  # This list has no limit size
])

rand_nums_list = collection1.sorted_list("SortedRandomNumbers")
names_list = collection1.sorted_list("SortedNames")

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

rand_nums_list.insert(nums)
names_list.insert(names)

print("\n==== Smallest 5 numbers: =====")
print(rand_nums_list.smallest(5)[1])

print("==== Biggest 5 numbers: =====")
print(rand_nums_list.biggest(5)[1])

        print("\n==== Sorted names: =====")
for name in names_list.smallest(100)[1]:
    print(name)
```
Expected Output:
```
==== Random numbers: =====
[10, 0, 14, 11, 13, 12, 4, 3, 1, 5, 2, 7, 9, 6, 8]

==== Smallest 5 numbers: =====
('SortedRandomNumbers', [0, 1, 2, 3, 4])
==== Biggest 5 numbers: =====
('SortedRandomNumbers', [10, 11, 12, 13, 14])

==== Sorted names: =====
Bill Gates
Donald Trump
Elon Musk
Jane Doe
Jeff Bezos
John Doe
Larry Ellison
Larry Page
Mark Zuckerberg
Sergey Brin
Steve Jobs
Tim Cook
```

### Stack

Stacks are simple array structures which only allows you to put new items and get them from top

```python
collection1.create_stacks([
    ("StackA", ValueType.Float, 5),
])

stack_a = collection1.stack("StackA")

stack_a.put([1.0, 2.3])
stack_a.put([3.1, 4.3, 5.6])

print(stack_a.pop(3))

print(stack_a.pop())
```
Expected Output:
```
('StackA', [5.6, 4.3, 3.1])
('StackA', [2.3])
```

### Fifo

Fifo is like a pipe where you are able to push items only for one side, and pull them in the same order they entered by the other side.

```python
collection1.create_fifos([
    ("Fifo1", ValueType.Bool, 5),
])

fifo1 = collection1.fifo("Fifo1")

fifo1.push([True, False, True])
fifo1.push([False, False])

print(fifo1.pull(3))

print(fifo1.pull(20))
```

Expected Output:
```
('Fifo1', [False, True, False])
('Fifo1', [True, False])
```
