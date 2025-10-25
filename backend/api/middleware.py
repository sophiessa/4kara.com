from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

@database_sync_to_async
def get_user_from_token(token_key):
    """
    Authenticates a user based on a DRF token key.
    Returns the user object or AnonymousUser.
    """
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Custom middleware for Django Channels to authenticate users via
    a token passed in the query string.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode('utf-8')
        parsed_query = parse_qs(query_string)
        token_key = parsed_query.get('token', [None])[0]
        if token_key:
            scope['user'] = await get_user_from_token(token_key)
            print(f"TokenAuthMiddleware: Authenticated user {scope['user']}")
        else:
            scope['user'] = AnonymousUser()
            print("TokenAuthMiddleware: No token provided, using AnonymousUser")
        return await self.app(scope, receive, send)