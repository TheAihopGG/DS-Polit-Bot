import argparse
from os.path import exists
from data.settings import *
# define errors
class TokenError(Exception): pass
class TokenNotProvided(TokenError): pass
class NoTokenFileProvided(TokenError): pass

def get_token() -> str:
    """
    # usage:
    token = get_token()

    It gets token from console, or from token file
    
    If token is not provided in console, and in file, it will raise 'TokenNotProvided'
    """
    # define parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help='Provide a bot token. Token will be cached in token file'
    )
    # parse args
    args = parser.parse_args()
    if args.token: # if token is not None update token file
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(args.token)
    else: # else get token from token file
        if exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as token_file:
                args.token = token_file.read()
            if not args.token: # if no token in token file raise exc
                raise TokenNotProvided(f'No token provided in token file. Path: {TOKEN_PATH}')
        else:
            raise NoTokenFileProvided(f'No token file provided in {TOKEN_PATH}')
    return args.token