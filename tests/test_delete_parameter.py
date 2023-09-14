import json
import responses

from jupiterone.client import JupiterOneClient


@responses.activate
def test_delete_parameter():

    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }

        response = {
            'data': {
                'setParameter': {
                    'success': True
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
    response = j1.delete_parameter('testKey')

    assert type(response) == dict
    assert type(response['success']) == bool
    assert response['success'] == True
