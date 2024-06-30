#!/usr/bin/env python3
# 
# PyTeamCity - A Python library for interacting with the TeamCity REST API.
# 
# Version: Alpha 0.1
# 

# Import the required libraries.
import requests
from requests.exceptions import HTTPError
import logging
import json

class PrettyJsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage()
        }
        return json.dumps(log_record, indent=4)

class PyTeamCity:
    # 
    # Constants
    # 
    # Authentication types.
    _AUTH_TYPES = {
        'TOKEN': {
            'description': 'Token based authentication'
        },
        'USER_PASS': {
            'description': 'Username and password based authentication'
        }
    }

    # ------------------------------

    # 
    # Global variables
    # 
    _auth_type:int = None
    _auth:tuple = None
    _api_url:str = None

    _body_format:str = None # json or xml
    _response_format:str = None # json or object
    _headers:str = {}

    _logger = logging.getLogger('PyTeamCity')

    def __init__(self, base_url:str=None, username:str=None, password:str=None, token=None, body_format='json', response_format:str='json'):
        try:
            # 
            # Configure the logger and format the logs as JSON.
            log_stream_handler = logging.StreamHandler()
            log_stream_handler.setFormatter(PrettyJsonFormatter(datefmt='%Y-%m-%d %H:%M:%S'))
            self._logger.addHandler(log_stream_handler)
            self._logger.propagate = False
            self._logger.setLevel(logging.INFO)

            # Check base_url provided.
            if not base_url:
                raise Exception('Base URL must be provided.')
            
            self._api_url = f'{base_url}/app/rest'

            # Check either json or xml is provided.
            if body_format not in ['json', 'xml']:
                raise Exception('Response format must be either json or xml. Default is json.')
            
            self._body_format = body_format.lower()
            self._headers['Accept'] = f'application/{self._body_format}'

            # Check the response format.
            if response_format not in ['json', 'text', 'object']:
                raise Exception('Response format must be either json, text or object. Default is json.')

            self._response_format = response_format.lower()

            # Check either a token or a username and password is provided.
            if not token and not username and not password:
                raise Exception('Either a token, or a username and password must be provided.')
            
            # If a token is provided, use it.
            if token:
                self._auth_type = 'TOKEN'
                self._auth = (token, '')
            else:
                self._auth_type = 'USER_PASS'
                self._auth = (username, password)
            
            # Log the successful initialization.
            auth_description = self._AUTH_TYPES[self._auth_type]['description']

            self._logger.debug(f'TeamCity object initialized. Url: {self._api_url}. Authentication: {auth_description}.')

        except Exception as e:
            self._logger.error(f'Error: {e}')
            raise

    def get_users(self, username:str=None, id:int=None, href:str=None, locator=None, fields:str="*"):
        try:
            # 
            # Parameter rules:
            # - username, id, href, locator: If none provided, assume all users are required.
            # - username, id, href, locator: If provided, only one of these can be provided.
            # - locator: If provided, nesting is within (), e.g. (username:myuser). All ( must be closed with ).
            # - fields: If not provided, defaults to *.
            # 

            # Check that either 0 (all users) or 1 (specific user/s) of username, id, href, or locator is provided.
            params_count = sum([1 for param in [username, id, href, locator] if param])
            if params_count == 0:
                self._logger.debug('Requesting all users.')  
            elif params_count > 1:
                raise Exception('Only one of username, id, href, or locator can be provided.')  
            
            # Check if locator is provided, the parantheses are balanced.
            if locator and locator.count('(') != locator.count(')'):
                raise Exception('Unbalanced parentheses in locator. Check that all ( are closed with ).')
            
            # Reset the fields to * if not provided.
            if not fields:
                fields = '*'
            
            # Construct the url depending on the parameters provided.
            url = f'{self._api_url}/users'
            url += f'?locator=username:{username}' if username else \
                   f'?locator=id:{id}' if id else \
                   f'?locator=href:{href}' if href else \
                   f'?locator:{locator}' if locator else ''
            
            url += f'?fields={fields}' if params_count == 0 else f'&fields={fields}'

            self._logger.debug(f'Request: {url}')

            headers = self._headers
            auth = self._auth

            params = {}

            # Make the request.
            response = requests.get(url=url, 
                                    auth=auth, 
                                    params=params, 
                                    headers=headers)
            response.raise_for_status()

            if self._response_format == 'json':
                self._logger.debug(f'Response: {response.json()}')
                return True, 'Success', response.json()
            elif self._response_format == 'text':
                self._logger.debug(f'Response: {response.text}')
                return True, 'Success', response.text
            else:
                self._logger.debug(f'Response: {response}')
                return True, 'Success', response
        
        except HTTPError as e:
            self._logger.error(f'HTTP Error: {e}')
            return False, 'Failure', e
        
        except Exception as e:
            self._logger.error(f'Error: {e}')
            return False, 'Failure', e

# 
# Main
# 
if __name__ == '__main__':
    # Set up the app logger. Formatted as a table.
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    tc = PyTeamCity(base_url='http://localhost:8111', username='replaceme', password='replaceme')
    
    result, message, response = tc.get_users(fields='**')

    if not result:
        logger.error(f'{message}')
        exit(1)
    
    # 
    # Look for any users with a role in the project scope.
    scope_exact = [ 'p:MyParentProject' ]
    scope_starts_with = [ f'{scope_exact[0]}_' ]   

    for user in response['user']:
        username, roles = user['username'], user['roles']['role']

        for role in roles:

            if role['scope'] in scope_exact or any([role['scope'].startswith(s) for s in scope_starts_with]):
                logger.info(f'Username: {username}\tRoleId: {role["roleId"]}\tScope: {role["scope"]}')
