from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    """Permit Insomnia's Bearer tab as well as DRF's standard Token header."""
    keyword = 'Bearer'
