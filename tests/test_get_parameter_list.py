import json
import responses

from jupiterone.client import JupiterOneClient


@responses.activate
def test_get_parameter_list():

    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }

        response = {
            'data': {
                'parameterList': {
                    'items': [
                        {
                            'name': 'name1',
                            'value': 1,
                            'secret': False,
                            'lastUpdatedOn': 'YYYY-MM-DDTHH:mm:ss.SSSZ'
                        },
                        {
                            'name': 'name2',
                            'value': '[REDACTED]',
                            'secret': True,
                            'lastUpdatedOn': 'YYYY-MM-DDTHH:mm:ss.SSSZ'
                        }
                    ],
                    'pageInfo': {
                        'endCursor': None,
                        'hasNextPage': False
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
    response = j1.get_parameter_list()

    assert type(response) == dict
    assert type(response['parameters']) == list
    assert type(response['parameters'][0]['name']) == str
    assert type(response['parameters'][0]['value']) in [str, int, float, bool, list]
    assert type(response['parameters'][0]['secret']) == bool
    assert type(response['parameters'][0]['lastUpdatedOn']) == str
    assert response['parameters'][0]['name'] == 'name1'
    assert response['parameters'][0]['value'] == 1
    assert response['parameters'][0]['secret'] == False
    assert response['parameters'][0]['lastUpdatedOn'] == 'YYYY-MM-DDTHH:mm:ss.SSSZ'
    assert type(response['parameters'][1]['name']) == str
    assert type(response['parameters'][1]['value']) in [str, int, float, bool, list]
    assert type(response['parameters'][1]['secret']) == bool
    assert type(response['parameters'][1]['lastUpdatedOn']) == str
    assert response['parameters'][1]['name'] == 'name2'
    assert response['parameters'][1]['value'] == '[REDACTED]'
    assert response['parameters'][1]['secret'] == True
    assert response['parameters'][1]['lastUpdatedOn'] == 'YYYY-MM-DDTHH:mm:ss.SSSZ'
