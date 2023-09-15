import json
import responses

from jupiterone.client import JupiterOneClient


@responses.activate
def test_get_parameter():

    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }

        response = {
            'data': {
                'parameter': {
                    'name': 'name',
                    'value': 1,
                    'secret': False,
                    'lastUpdatedOn': 'YYYY-MM-DDTHH:mm:ss.SSSZ'
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
    response = j1.get_parameter('testKey')

    assert type(response) == dict
    assert type(response['name']) == str
    assert type(response['value']) in [str, int, float, bool, list]
    assert type(response['secret']) == bool
    assert type(response['lastUpdatedOn']) == str
    assert response['name'] == 'name'
    assert response['value'] == 1
    assert response['secret'] == False
    assert response['lastUpdatedOn'] == 'YYYY-MM-DDTHH:mm:ss.SSSZ'
