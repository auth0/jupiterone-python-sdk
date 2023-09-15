# JupiterOne Python SDK

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)


A Python library for the [JupiterOne API](https://support.jupiterone.io/hc/en-us/articles/360022722094-JupiterOne-Platform-API).

## Installation

Requires Python 3.6+

`pip install jupiterone`


## Usage

##### Create a new client:

```python
from jupiterone import JupiterOneClient

j1 = JupiterOneClient(
    account='<yourAccountId>',
    token='<yourApiToken>'
)
```

##### Execute a query:

```python
QUERY = 'FIND Host'
query_result = j1.query_v1(QUERY)

# Using LIMIT and SKIP for pagination
query_result = j1.query_v1(QUERY, limit=5, skip=5)

# Including deleted entities
query_result = j1.query_v1(QUERY, include_deleted=True)

# Tree query
QUERY = 'FIND Host RETURN TREE'
query_result = j1.query_v1(QUERY)
```

##### Create an entity:

Note that the CreateEntity mutation behaves like an upsert, so an non-existant entity will be created or an existing entity will be updated.

```python
properties = {
    'myProperty': 'myValue',
    'tag.myTagProperty': 'value_will_be_a_tag'
}

entity = j1.create_entity(
   entity_key='my-unique-key',
   entity_type='my_type',
   entity_class='MyClass',
   properties=properties,
   timestamp=int(time.time()) * 1000 # Optional, defaults to current datetime
)
print(entity['entity'])
```


#### Update an existing entity:
Only send in properties you want to add or update, other existing properties will not be modified.

```python
properties = {
    'newProperty': 'newPropertyValue'
}

j1.update_entity(
    entity_id='<id-of-entity-to-update>',
    properties=properties
)
```


#### Delete an entity:

```python
j1.delete_entity(entit_id='<id-of-entity-to-delete>')
```

##### Create a relationship

```python
j1.create_relationship(
    relationship_key='this_entity_relates_to_that_entity',
    relationship_type='my_relationship_type',
    relationship_class='MYRELATIONSHIP',
    from_entity_id='<id-of-source-entity>',
    to_entity_id='<id-of-destination-entity>'
)
```

##### Delete a relationship

```python
j1.delete_relationship(relationship_id='<id-of-relationship-to-delete>')
```

##### Create a parameter, or modify an existing parameter

```python
set_status = j1.set_parameter(
    name='name_of_parameter', # If 'name_of_parameter' already exists, the value is modified
    value='value_to_be_stored', # Can be a string, number, boolean, or list
    secret=(True|False) # Optional, defaults to False
)
```

##### Get a stored parameter

Parameters are stored as a dictionary in the format `{'name': $parameterName, 'value': $parameterValue, 'secret': $isParameterSecret, 'lastUpdatedOn': $lastUpdateTimestamp}`

```python
parameter = j1.get_parameter(
    name='name_of_parameter'
)

print(parameter)
print(parameter['value']) # If parameter['secret'] = True, then parameter['value'] will be '[REDACTED]'
```

##### Get all stored parameters

```python
parameterList = j1.get_parameter_list()

print(parameterList) # Returns a dictionary in format {'parameters': list_of_parameters}
print(parameterList[0]) # Returns the first parameter as a dictionary
print(parameterList[0]['value']) # Returns the stored value of the first parameter
```

##### Delete a stored parameter

```python
j1.delete_parameter(
    name='name_of_parameter'
)
```