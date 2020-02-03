import json
import pytest
import responses

from jupiterone.client import JupiterOneClient
from jupiterone.constants import CREATE_ENTITY


@responses.activate
def test_tree_query_v1():

    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }

        response = {
            'data': {
                'deleteRelationship': {
                    'relationship': {
                        '_id': '1'
                    }, 
                    'edge': {
                        'id': '1',
                        'toVertexId': '1',
                        'fromVertexId': '2',
                        'relationship': {
                            '_id': '1'
                        },
                        'properties': {}
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
    response = j1.delete_relationship('1')

    assert type(response) == dict
    assert type(response['relationship']) == dict
    assert response['relationship']['_id'] == '1'
    assert response['edge']['toVertexId'] == '1'
    assert response['edge']['fromVertexId'] == '2'
