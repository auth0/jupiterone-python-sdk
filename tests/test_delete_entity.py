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
                'deleteEntity': {
                    'entity': {
                        '_id': '1'
                    },
                    'vertex': {
                        'id': '1',
                        'entity': {
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
    response = j1.delete_entity('1')

    assert type(response) == dict
    assert type(response['entity']) == dict
    assert type(response['vertex']) == dict
    assert response['entity']['_id'] == '1'
