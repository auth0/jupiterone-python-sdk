import json
import pytest
import responses
from collections import Counter

from jupiterone.client import JupiterOneClient
from jupiterone.constants import QUERY_V1
from jupiterone.errors import JupiterOneApiError

def build_results(response_code: int = 200, cursor: str = None, max_pages: int = 1):
    pages = Counter(requests=0)

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

        if cursor is not None and pages.get('requests') < max_pages:
            response['data']['queryV1']['cursor'] = cursor

        pages.update(requests=1)

        return (response_code, headers, json.dumps(response))

    return request_callback


def build_error_results(response_code: int, response_content, response_type: str = 'application/json'):
    def request_callback(request):
        headers = {
            'Content-Type': response_type
        }
        return response_code, headers, response_content

    return request_callback


@responses.activate
def test_execute_query():

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(),
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
def test_limit_skip_query_v1():

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    response = j1.query_v1(
        query=query,
        limit=250,
        skip=0
    )

    assert type(response) == dict
    assert len(response['data']) == 1
    assert type(response['data']) == list
    assert response['data'][0]['entity']['_id'] == '1'

@responses.activate
def test_cursor_query_v1():

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(cursor='cursor_value'),
        content_type='application/json',
    )

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"

    response = j1.query_v1(
        query=query,
    )

    assert type(response) == dict
    assert len(response['data']) == 2
    assert type(response['data']) == list
    assert response['data'][0]['entity']['_id'] == '1'

@responses.activate
def test_limit_skip_tree_query_v1():

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
    response = j1.query_v1(
        query=query,
        limit=250,
        skip=0
    )

    assert type(response) == dict
    assert 'edges' in response
    assert 'vertices' in response
    assert type(response['edges']) == list
    assert type(response['vertices']) == list
    assert response['vertices'][0]['id'] == '1'

@responses.activate
def test_cursor_tree_query_v1():

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

@responses.activate
def test_retry_on_limit_skip_query():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(response_code=429),
        content_type='application/json',
    )

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(response_code=503),
        content_type='application/json',
    )

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    response = j1.query_v1(
        query=query,
        limit=250,
        skip=0
    )

    assert type(response) == dict
    assert len(response['data']) == 1
    assert type(response['data']) == list
    assert response['data'][0]['entity']['_id'] == '1'

@responses.activate
def test_retry_on_cursor_query():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(response_code=429),
        content_type='application/json',
    )

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(response_code=503),
        content_type='application/json',
    )

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    response = j1.query_v1(
        query=query
    )

    assert type(response) == dict
    assert len(response['data']) == 1
    assert type(response['data']) == list
    assert response['data'][0]['entity']['_id'] == '1'

@responses.activate
def test_avoid_retry_on_limit_skip_query():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(response_code=404),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    with pytest.raises(JupiterOneApiError):
        j1.query_v1(
            query=query,
            limit=250,
            skip=0
        )

@responses.activate
def test_avoid_retry_on_cursor_query():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(response_code=404),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"
    with pytest.raises(JupiterOneApiError):
        j1.query_v1(
            query=query
        )

@responses.activate
def test_warn_limit_and_skip_deprecated():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_results(),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    query = "find Host with _id='1'"

    with pytest.warns(DeprecationWarning):
        j1.query_v1(
            query=query,
            limit=250,
            skip=0
        )


@responses.activate
def test_unauthorized_query_v1():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_error_results(401, b'Unauthorized', 'text/plain'),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='bogusToken')
    query = "find Host with _id='1' return tree"

    with pytest.raises(JupiterOneApiError) as exc_info:
        j1.query_v1(query)

    assert exc_info.value.args[0] == 'JupiterOne API query is unauthorized, check credentials.'


@responses.activate
def test_unexpected_string_error_query_v1():
    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_error_results(500, 'String exception on server', 'text/plain'),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='bogusToken')
    query = "find Host with _id='1' return tree"

    with pytest.raises(JupiterOneApiError) as exc_info:
        j1.query_v1(query)

    assert exc_info.value.args[0] == '500:String exception on server'


@responses.activate
def test_unexpected_json_error_query_v1():
    error_json = {
        'error': 'Bad Gateway'
    }

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_error_results(502, json.dumps(error_json), ),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='bogusToken')
    query = "find Host with _id='1' return tree"

    with pytest.raises(JupiterOneApiError) as exc_info:
        j1.query_v1(query)

    assert exc_info.value.args[0] == '502:Bad Gateway'


@responses.activate
def test_unexpected_json_errors_query_v1():
    errors_json = {
        'errors': ['First error', 'Second error', 'Third error']
    }

    responses.add_callback(
        responses.POST, 'https://api.us.jupiterone.io/graphql',
        callback=build_error_results(500, json.dumps(errors_json), ),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='bogusToken')
    query = "find Host with _id='1' return tree"

    with pytest.raises(JupiterOneApiError) as exc_info:
        j1.query_v1(query)

    assert exc_info.value.args[0] == "500:['First error', 'Second error', 'Third error']"
