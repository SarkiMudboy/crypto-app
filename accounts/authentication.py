from rest_framework.authentication import TokenAuthentication

class BearerAuthentication(TokenAuthentication):
    """changing the token keyword to bearer"""

    keyword = 'Bearer'