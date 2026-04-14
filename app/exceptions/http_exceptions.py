"""
HTTP Domain Exceptions.

Custom exception classes that represent standard HTTP error states. 
These are caught by the 'Global Exception Handler' to return 
consistent status codes to the client.
"""
class ForbiddenException(Exception):
    pass

class NotFoundException(Exception):
    pass

class UnauthorizedException(Exception):
    pass
