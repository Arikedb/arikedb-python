# Arikedb Python Library

Welcome to the ArikeDB Python library! This library provides an interface to interact with the Arike Database, an advanced real-time database solution. This documentation will guide you through the process of setting up and using the library effectively.

## Getting Started

### Installation

To use the ArikeDB Rust library, install it using pip:

```bash
~$ pip install arikedb
```

### Connecting to ArikeDB

To connect to an ArikeDB server instance, bring `ArikedbClient` into scope, instantiate it and call the `connect` method.

#### Basic Connection

```python
from arikedb import ArikedbClient


if __name__ == "__main__":
    client = ArikedbClient().connect(host="127.0.0.1", port=6923)
```

#### Connection with Authentication

If the server requires authentication, you need to authenticate after connecting.

```python
from arikedb import ArikedbClient


if __name__ == "__main__":
    client = ArikedbClient().connect(host="127.0.0.1", port=6923)
    client.authenticate(username="username", password="password")
```

### Creating Collections

ArikeDB organizes data into collections. Each collection has a name and a set of variables. To create multiple collections in a single call:

```python
client.create_collections(names=["collection1", "collection2", "collection3", "collection4"])
```

### Deleting Collections

```python
client.delete_collections(names=["collection3", "collection4"])
```

### Listing Collections

```python
collections = client.list_collections().collections
for collection in collections:
    print(collection.__dict__)
```
Output:
```
{'name': 'collection1'}
{'name': 'collection2'}
```

### Creating Variables

```python
client.create_variables(
    collection="collection1",
    variables=[
        Variable(name="var1", vtype=VariableType.I32, buffer_size=10),
        {"name": "var2", "vtype": VariableType.I32, "buffer_size": 5},
        Variable(name="var3", vtype=VariableType.I32, buffer_size=10),
        Variable(name="var4", vtype=VariableType.I32, buffer_size=10),
    ]
)
```

### Deleting Variables

```python
client.delete_variables(
    collection="collection1",
    variables=["var3", "var4"]
)
```

### Listing Variables

```python
variables = client.list_variables(collection="collection1").variables
for variable in variables:
    print(variable.__dict__)
```
Output:
```
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'buffer_size': 10}
{'name': 'var2', 'vtype': <VariableType.I32: 2>, 'buffer_size': 5}
```

### Setting Variables Values

```python
client.set_variables(
    collection="collection1",
    variables=["var1", "var2"],
    epoch=Epoch.Microsecond,
    timestamp=int(time.time() * 1e6),
    values=[4, 7]
)
```

### Getting Variables Values

```python
datapoints = client.get_variables(
    collection="collection1",
    variables=["var1", "var2"],
    epoch=Epoch.Nanosecond,
    derived_order=0
).data_points
for datapoint in datapoints:
    print(datapoint.__dict__)
```
Output:
```
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720990632467691000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 4}
{'name': 'var2', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720990632467691000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 7}
```

### Subscribe to Variables Events
Events are generated over variables when they ar set and event condition happens.

```python
def on_data(data_point):
    print(data_point.__dict__)

client.subscribe_variables(
    collection="collection1",
    variables=["var1", "var2"],
    events=[
        VarEvent(Event.OnRise),
        VarEvent(Event.OnValueEqVal, value="56")
    ],
    callback=on_data,
    thread_kwargs={"daemon": True}
)

for i in range(10):
    client.set_variables(
        collection="collection1",
        variables=["var1", "var2"],
        epoch=Epoch.Microsecond,
        timestamp=int(time.time() * 1e6),
        values=[(50 + i), (60 - i)]
    )
    time.sleep(1)
```
Output:
```
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992049653048000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 50}
{'name': 'var2', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992049653048000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 60}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992050668472000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 51}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992051679201000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 52}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992052686982000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 53}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992053697670000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 54}
{'name': 'var2', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992053697670000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 56}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992054719111000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 55}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992055729433000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 56}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992056749812000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 57}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992057773916000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 58}
{'name': 'var1', 'vtype': <VariableType.I32: 2>, 'timestamp': 1720992058795081000, 'epoch': <Epoch.Nanosecond: 3>, 'value': 59}
```