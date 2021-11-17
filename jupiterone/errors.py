from enum import Enum

class JupiterOneClientError(Exception):
    """ Raised when error creating client """    

class JupiterOneApiRetryError(Exception):
    """ Used to trigger retry on rate limit """

class JupiterOneApiError(Exception):
    """ Raised when API returns error response """

class JupiterOneQueryTimeoutError(Exception):
    """ Raised when query has timed out """