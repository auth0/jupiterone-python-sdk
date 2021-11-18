J1QL_SKIP_COUNT = 250
J1QL_LIMIT_COUNT = 250

QUERY_V1 = """
  query J1QL($query: String!, $variables: JSON, $dryRun: Boolean, $includeDeleted: Boolean) {
    queryV1(query: $query, variables: $variables, dryRun: $dryRun, includeDeleted: $includeDeleted) {
      type
      data
    }
  }
"""

CURSOR_QUERY_V1 = """
  query J1QL_v2($query: String!, $variables: JSON, $flags: QueryV1Flags, $includeDeleted: Boolean, $cursor: String) {
    queryV1(
      query: $query
      variables: $variables
      deferredResponse: DISABLED
      flags: $flags
      includeDeleted: $includeDeleted
      cursor: $cursor
    ) {
      type
      data
      cursor
      __typename
    }
  }
"""

CREATE_ENTITY = """
  mutation CreateEntity(
    $entityKey: String!
    $entityType: String!
    $entityClass: [String!]!
    $properties: JSON
  ) {
    createEntity(
      entityKey: $entityKey
      entityType: $entityType
      entityClass: $entityClass
      properties: $properties
    ) {
      entity {
        _id
      }
      vertex {
        id
        entity {
          _id
        }
      }
    }
  }
"""

DELETE_ENTITY = """
  mutation DeleteEntity($entityId: String!, $timestamp: Long) {
    deleteEntity(entityId: $entityId, timestamp: $timestamp) {
      entity {
        _id
      }
      vertex {
        id
        entity {
          _id
        }
        properties
      }
    }
  }
"""

UPDATE_ENTITY = """
  mutation UpdateEntity($entityId: String!, $properties: JSON) {
    updateEntity(entityId: $entityId, properties: $properties) {
      entity {
        _id
      }
      vertex {
        id
      }
    }
  }
"""

CREATE_RELATIONSHIP = """
  mutation CreateRelationship(
    $relationshipKey: String!
    $relationshipType: String!
    $relationshipClass: String!
    $fromEntityId: String!
    $toEntityId: String!
    $properties: JSON
  ) {
    createRelationship(
      relationshipKey: $relationshipKey
      relationshipType: $relationshipType
      relationshipClass: $relationshipClass
      fromEntityId: $fromEntityId
      toEntityId: $toEntityId
      properties: $properties
    ) {
      relationship {
        _id
      }
      edge {
        id
        toVertexId
        fromVertexId
        relationship {
          _id
        }
        properties
      }
    }
  }
"""

DELETE_RELATIONSHIP = """
  mutation DeleteRelationship($relationshipId: String! $timestamp: Long) {
    deleteRelationship (relationshipId: $relationshipId, timestamp: $timestamp) {
      relationship {
        _id
      }
      edge {
        id
        toVertexId
        fromVertexId
        relationship {
          _id
        }
        properties
      }
    }
  }
"""