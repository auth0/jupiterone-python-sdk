import json
import pytest
import responses

from jupiterone.client import JupiterOneClient
from jupiterone.constants import QUERY_V1

def request_callback(request):
    headers = {
        'Content-Type': 'application/json'
    }

    response = {
        'data': {
            'queryV1': {
                'type': 'list',
                'data': [
                    {
                        'id': '1',
                        'entity': {
                            '_rawDataHashes': '1',
                            '_integrationDefinitionId': '1',
                            '_integrationName': '1',
                            '_beginOn': 1580482083079,
                            'displayName': 'host1',
                            '_class': ['Host'],
                            '_scope': 'aws_instance',
                            '_version': 1,
                            '_integrationClass': 'CSP',
                            '_accountId': 'testAccount',
                            '_id': '1',
                            '_key': 'key1',
                            '_type': ['aws_instance'],
                            '_deleted': False,
                            '_integrationInstanceId': '1',
                            '_integrationType': 'aws',
                            '_source': 'integration-managed',
                            '_createdOn': 1578093840019
                        },
                        'properties': {
                            'id': 'host1',
                            'active': True
                        }
                    }
                ]
            }
        }
    }
    return (200, headers, json.dumps(response))


@responses.activate
def test_execute_query():

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    variables = {
        'query': query,
        'includeDeleted': False
    }

    response = j1._execute_query(
        query=QUERY_V1,
        variables=variables
    )
    assert 'data' in response
    assert 'queryV1' in response['data']
    assert len(response['data']['queryV1']['data']) == 1
    assert type(response['data']['queryV1']['data']) == list
    assert response['data']['queryV1']['data'][0]['entity']['_id'] == '1' 


@responses.activate
def test_query_v1():

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    response = j1.query_v1(query)

    assert type(response) == dict
    assert len(response['data']) == 1
    assert type(response['data']) == list
    assert response['data'][0]['entity']['_id'] == '1'


@responses.activate
def test_401():
    with pytest.raises(Exception) as ex:

        def response_401_callback(r):
            headers = {
                'Content-Type': 'application/json'
            }

            response = {
                'test': ['Unauthorized']
            }
            return (401, headers, json.dumps(response))

        responses.add_callback(
            responses.POST, 'https://api.us.jupiterone.io/graphql',
            callback=response_401_callback,
            content_type='application/text',
        )

        j1 = JupiterOneClient(account='testAccount', token='testToken')
        query = "find Host with _id='1'"
        j1.query_v1(query)
        
    assert '401: Unauthorized. Please supply a valid token' in str(ex.value)


@responses.activate
def test_tree_query_v1():

    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }

        response = {
            'data': {
                'queryV1': {
                    'type': 'tree',
                    'data': {
                        'vertices': [
                            {
                                'id': '1',
                                'entity': {},
                                'properties': {}
                            }
                        ],
                        'edges': []
                    }
                }
            }
        }

        return (200, headers, json.dumps(response))

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1' return tree"
    response = j1.query_v1(query)

    assert type(response) == dict 
    assert 'edges' in response
    assert 'vertices' in response
    assert type(response['edges']) == list
    assert type(response['vertices']) == list
    assert response['vertices'][0]['id'] == '1'
    