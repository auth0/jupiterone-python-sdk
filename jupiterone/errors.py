
class JupiterOneClientError(Exception):
    """ Raised when error creating client """    

class JupiterOneApiRetryError(Exception):
    """ Used to trigger retry on rate limit """

class JupiterOneApiError(Exception):
    """ Raised when API returns error response """