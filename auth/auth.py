#references and sources for this code
'''
code provided/demonstrated in Lessons 2 and 4 of Identity and Access Management
https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
https://auth0.com/docs/quickstart/backend/python
'''
from os import environ
from ast import AugAssign
import json
from functools import wraps
from lib2to3.pgen2 import token
from urllib.request import urlopen
from flask import abort, request
from jose import jwt


AUTH0_DOMAIN = environ['DOMAIN']#'dav-eng-code-testing.eu.auth0.com'
API_AUDIENCE = environ['API_AUDIENCE']
ALGORITHMS = environ['ALGORITHMS']

#Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

#get the token from the authorisation header in the request
def get_token_auth_header():
    
    auth_header=request.headers.get('Authorization',None)
    if not auth_header:
        raise AuthError({
            'code':'authorization_header_missing',
            'description':'Authorization header is missing'
            },401)
        
    parts = auth_header.split(' ')

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code':'invalid_header',
            'description':'Authorization header is missing Bearer'
            },401)
    elif len(parts)!=2:
        raise AuthError({
            'code':'invalid_header',
            'description':'Authorization header should have only two parts'
            },401)

    token = parts[1]
    return token

#verify the jwt to ensure it is valid and get the payload
def verify_decode_jwt(token):
    jsonurl = urlopen('https://'+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks=json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key={}
    for key in jwks['keys']:
        if key['kid']==unverified_header['kid']:
            rsa_key={
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
            }
    if rsa_key:
        try:
            payload=jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://'+AUTH0_DOMAIN+'/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({'code':'token_expired',
                            'description':'token is expired'},401)
        except jwt.ExpiredSignatureError:
            raise AuthError({'code':'invalid_claims',
                            'description':'check audience and issuer'},401)
        except jwt.ExpiredSignatureError:
            raise AuthError({'code':'invalid_header',
                            'description':'Unable to parse auth header'},401)

    raise AuthError({
        'code':'invalid_header',
        'description':'cannot find key'},401)

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({'code':'bad request',
                        'description':'missing permissions'},400)
    if permission not in payload['permissions']:
        raise AuthError({'code':'forbidden',
                        'description':'you do not have permission to do that'},403)
    return True


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            #need function to get the token from the authorisation header in the request
            jwt = get_token_auth_header()
            #decode the token to get the payload
            payload = verify_decode_jwt(jwt)
            #check the payload contains the required permission
            check_permissions(permission, payload)

            
            return f(payload, *args,**kwargs)
        return wrapper
    return requires_auth_decorator
