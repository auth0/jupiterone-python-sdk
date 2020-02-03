import pytest

from jupiterone.client import JupiterOneClient


def test_missing_account():

    with pytest.raises(Exception) as ex:
        j1 = JupiterOneClient(token='123')
        assert 'account is required' in str(ex.value)


def test_missing_token():

    with pytest.raises(Exception) as ex:
        j1 = JupiterOneClient(account='test')
        assert 'token is required' in str(ex.value)