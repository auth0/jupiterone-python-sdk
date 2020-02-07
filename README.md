# JupiterOne Python SDK

A Python library for the JupiterOne API.

Python 3.6+


## Usage

Create a new client:

```
from jupiterone import JupiterOneClient

j1 = JupiterOneClient(
    account='<yourAccountId>',
    token='<yourApiToken>'
)
```

Execute a query:

```
QUERY = 'FIND Host'

query_result = j1.query_v1(QUERY)

# Using LIMIT and SKIP for pagination

query_result = j1.query_v1(QUERY, limit=5, skip=5)

```