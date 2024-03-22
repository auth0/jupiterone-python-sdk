""" Python SDK for JupiterOne GraphQL API """
# pylint: disable=W0212,no-name-in-module
# see https://github.com/PyCQA/pylint/issues/409

import json
from typing import Dict, List
import time

import requests
from retrying import retry
from warnings import warn

from jupiterone.errors import (
    JupiterOneClientError,
    JupiterOneApiRetryError,
    JupiterOneApiError
)

from jupiterone.constants import (
    J1QL_SKIP_COUNT,
    J1QL_LIMIT_COUNT,
    J1QL_DEFERRED_RESPONSE_POLL_TIMEOUT,
    DEFERRED_RESPONSE_STATUS_COMPLETED,
    QUERY_V1,
    CREATE_ENTITY,
    DELETE_ENTITY,
    UPDATE_ENTITY,
    CREATE_RELATIONSHIP,
    DELETE_RELATIONSHIP,
    CURSOR_QUERY_V1
)

def retry_on_429(exc):
    """ Used to trigger retry on rate limit """
    return isinstance(exc, JupiterOneApiRetryError)


class JupiterOneClient:
    """ Python client class for the JupiterOne GraphQL API """
    # pylint: disable=too-many-instance-attributes

    DEFAULT_URL = 'https://api.us.jupiterone.io'

    RETRY_OPTS = {
        'wait_exponential_multiplier': 1000,
        'wait_exponential_max': 10000,
        'stop_max_delay': 300000,
        'retry_on_exception': retry_on_429
    }

    def __init__(self, account: str = None, token: str = None, url: str = DEFAULT_URL):
        self.account = account
        self.token = token
        self.url = url
        self.query_endpoint = self.url + '/graphql'
        self.rules_endpoint = self.url + '/rules/graphql'
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'LifeOmic-Account': self.account
        }

    @property
    def account(self):
        """ Your JupiterOne account ID """
        return self._account

    @account.setter
    def account(self, value: str):
        """ Your JupiterOne account ID """
        if not value:
            raise JupiterOneClientError('account is required')
        self._account = value

    @property
    def token(self):
        """ Your JupiteOne access token """
        return self._token

    @token.setter
    def token(self, value: str):
        """ Your JupiteOne access token """
        if not value:
            raise JupiterOneClientError('token is required')
        self._token = value

    # pylint: disable=R1710
    @retry(**RETRY_OPTS)
    def _execute_query(self, query: str, variables: Dict = None) -> Dict:
        """ Executes query against graphql endpoint """

        data = {
            'query': query
        }
        if variables:
            data.update(variables=variables)

        response = requests.post(self.query_endpoint, headers=self.headers, json=data)

        # It is still unclear if all responses will have a status
        # code of 200 or if 429 will eventually be used to 
        # indicate rate limitting.  J1 devs are aware.
        if response.status_code == 200:
            if response._content:
                content = json.loads(response._content)
                if 'errors' in content:
                    errors = content['errors']
                    if len(errors) == 1:
                        if '429' in errors[0]['message']:
                            raise JupiterOneApiRetryError('JupiterOne API rate limit exceeded')
                    raise JupiterOneApiError(content.get('errors'))
                return response.json()

        elif response.status_code == 401:
            raise JupiterOneApiError('JupiterOne API query is unauthorized, check credentials.')

        elif response.status_code in [429, 503]:
            raise JupiterOneApiRetryError('JupiterOne API rate limit exceeded')

        else:
            content = response._content
            if isinstance(content, (bytes, bytearray)):
                content = content.decode("utf-8")
            if 'application/json' in response.headers.get('Content-Type', 'text/plain'):
                data = json.loads(content)
                content = data.get('error', data.get('errors', content))
            raise JupiterOneApiError('{}:{}'.format(response.status_code, content))

    def _cursor_query(self, query: str, cursor: str = None, include_deleted: bool = False, deferred_response: bool = False) -> Dict:
        """ Performs a V1 graph query using cursor pagination
            args:
                query (str): Query text
                cursor (str): A pagination cursor for the initial query
                include_deleted (bool): Include recently deleted entities in query/search
                deferred_response (bool): This option allows for a deferred response to be returned
        """

        results: List = []
        while True:
            variables = {
                'query': query,
                'includeDeleted': include_deleted,
                'deferredResponse': 'FORCE' if deferred_response else 'DISABLED'
            }

            if cursor is not None:
                variables['cursor'] = cursor

            response = self._execute_query(query=CURSOR_QUERY_V1, variables=variables)
            result_type = response['data']['queryV1']['type']

            if result_type == "deferred":
                result_url = ""
                while True:
                    status_url = response['data']['queryV1']['url']
                    status_response = requests.get(status_url, headers=self.headers)

                    if status_response.status_code == 200:
                        status_response_content = json.loads(status_response._content)
                        if status_response_content["status"] == DEFERRED_RESPONSE_STATUS_COMPLETED:
                            result_url = status_response_content["url"]
                            break
                        else:
                            time.sleep(J1QL_DEFERRED_RESPONSE_POLL_TIMEOUT)
                    else:
                        status_response.raise_for_status()

                if result_url:
                    result_response = requests.get(result_url, headers=self.headers)
                    if status_response.status_code == 200:
                        result_response_content = json.loads(result_response._content)

                        results.extend(result_response_content["data"])

                        if "cursor" in result_response_content and result_response_content["cursor"] is not None:
                            cursor = result_response_content['cursor']
                        else:
                            break
                    else:
                        status_response.raise_for_status()
            else:
                data = response['data']['queryV1']['data']

                if 'vertices' in data and 'edges' in data:
                    return data

                results.extend(data)

                if 'cursor' in response['data']['queryV1'] and response['data']['queryV1']['cursor'] is not None:
                    cursor = response['data']['queryV1']['cursor']
                else:
                    break

        return {'data': results}

    def _limit_and_skip_query(self, query: str, skip: int = J1QL_SKIP_COUNT, limit: int = J1QL_LIMIT_COUNT, include_deleted: bool = False) -> Dict:
        results: List = []
        page: int = 0

        while True:
            variables = {
                'query': f"{query} SKIP {page * skip} LIMIT {limit}",
                'includeDeleted': include_deleted
            }
            response = self._execute_query(
                query=QUERY_V1,
                variables=variables
            )

            data = response['data']['queryV1']['data']

            # If tree query then no pagination
            if 'vertices' in data and 'edges' in data:
                return data

            if len(data) < J1QL_SKIP_COUNT:
                results.extend(data)
                break

            results.extend(data)
            page += 1

        return {'data': results}

    def query_v1(self, query: str, **kwargs) -> Dict:
        """ Performs a V1 graph query
            args:
                query (str): Query text
                skip (int):  Skip entity count
                limit (int): Limit entity count
                cursor (str): A pagination cursor for the initial query
                include_deleted (bool): Include recently deleted entities in query/search
                deferred_response (bool): Set it True to allow 'FORCE' on the deferredResponse property. According to the documentation (https://docs.jupiterone.io/api/entity-relationship-queries): It is highly recommended that all automated processes use the deferredResponse='FORCE' option when issuing J1QL queries.
        """
        uses_limit_and_skip: bool = 'skip' in kwargs.keys() or 'limit' in kwargs.keys()
        skip: int = kwargs.pop('skip', J1QL_SKIP_COUNT)
        limit: int = kwargs.pop('limit', J1QL_LIMIT_COUNT)
        include_deleted: bool = kwargs.pop('include_deleted', False)
        cursor: str = kwargs.pop('cursor', None)
        deferred_response: bool = kwargs.pop('deferred_response', False)

        if uses_limit_and_skip:
            warn('limit and skip pagination is no longer a recommended method for pagination. To read more about using cursors checkout the JupiterOne documentation: https://support.jupiterone.io/hc/en-us/articles/360022722094#entityandrelationshipqueries', DeprecationWarning, stacklevel=2)
            return self._limit_and_skip_query(
                query=query,
                skip=skip,
                limit=limit,
                include_deleted=include_deleted
            )
        else:
            return self._cursor_query(
                query=query,
                cursor=cursor,
                include_deleted=include_deleted,
                deferred_response=deferred_response
            )

    def create_entity(self, **kwargs) -> Dict:
        """ Creates an entity in graph.  It will also update an existing entity.

        args:
            entity_key (str): Unique key for the entity
            entity_type (str): Value for _type of entity
            entity_class (str): Value for _class of entity
            timestamp (int): Specify createdOn timestamp
            properties (dict): Dictionary of key/value entity properties
        """
        variables = {
            'entityKey': kwargs.pop('entity_key'),
            'entityType': kwargs.pop('entity_type'),
            'entityClass': kwargs.pop('entity_class')
        }

        timestamp: int = kwargs.pop('timestamp', None)
        properties: Dict = kwargs.pop('properties', None)

        if timestamp:
            variables.update(timestamp=timestamp)
        if properties:
            variables.update(properties=properties)

        response = self._execute_query(
            query=CREATE_ENTITY,
            variables=variables
        )
        return response['data']['createEntity']

    def delete_entity(self, entity_id: str = None) -> Dict:
        """ Deletes an entity from the graph.  Note this is a hard delete.

        args:
            entity_id (str): Entity ID for entity to delete
        """
        variables = {
            'entityId': entity_id
        }
        response = self._execute_query(DELETE_ENTITY, variables=variables)
        return response['data']['deleteEntity']

    def update_entity(self, entity_id: str = None, properties: Dict = None) -> Dict:
        """
        Update an existing entity.

        args:
            entity_id (str): The _id of the entity to udate
            properties (dict): Dictionary of key/value entity properties
        """
        variables = {
            'entityId': entity_id,
            'properties': properties
        }
        response = self._execute_query(UPDATE_ENTITY, variables=variables)
        return response['data']['updateEntity']

    def create_relationship(self, **kwargs) -> Dict:
        """
        Create a relationship (edge) between two entities (veritces).

        args:
            relationship_key (str): Unique key for the relationship
            relationship_type (str): Value for _type of relationship
            relationship_class (str): Value for _class of relationship
            from_entity_id (str): Entity ID of the source vertex
            to_entity_id (str): Entity ID of the destination vertex
        """
        variables = {
            'relationshipKey': kwargs.pop('relationship_key'),
            'relationshipType': kwargs.pop('relationship_type'),
            'relationshipClass': kwargs.pop('relationship_class'),
            'fromEntityId': kwargs.pop('from_entity_id'),
            'toEntityId': kwargs.pop('to_entity_id')
        }

        properties = kwargs.pop('properties', None)
        if properties:
            variables['properties'] = properties

        response = self._execute_query(
            query=CREATE_RELATIONSHIP,
            variables=variables
        )
        return response['data']['createRelationship']

    def delete_relationship(self, relationship_id: str = None):
        """ Deletes a relationship between two entities.

        args:
            relationship_id (str): The ID of the relationship
        """
        variables = {
            'relationshipId': relationship_id
        }

        response = self._execute_query(
            DELETE_RELATIONSHIP,
            variables=variables
        )
        return response['data']['deleteRelationship']
