#!/usr/bin/env python3

import logging
import yaml
import json

from modules.PyTeamCity import PyTeamCity

# Generic log formatter.
class LogFormatter(logging.Formatter):
    datefmt:str = None
    mesgfmt:str = None
    indent:int = None

    def __init__(self, date_format:str=None, mesg_format:str=None, json_indent:int=None):
        if not date_format: self.datefmt = '%Y-%m-%d %H:%M:%S'
        
        if not mesg_format in ('text', 'json', 'csv'):
            self.mesgfmt = 'json'
        else:
            self.mesgfmt = mesg_format
        
        # Ensure the indent is between 0 and 10.
        if json_indent is not None and json_indent >= 0 and json_indent <= 10:
            self.indent = json_indent
        else:
            self.indent = 0
    
    def format(self, record):
        if self.mesgfmt == 'text':
            return f'{self.formatTime(record, self.datefmt)} [{record.levelname}] {record.getMessage()}'
        elif self.mesgfmt == 'csv':
            return f'{self.formatTime(record, self.datefmt)},{record.levelname},{record.getMessage()}'
        elif self.mesgfmt == 'json':
            if self.indent:
                return json.dumps({
                    'timestamp': self.formatTime(record, self.datefmt),
                    'level': record.levelname,
                    'message': record.getMessage()
                }, indent=self.indent)
            else:
                return json.dumps({
                    'timestamp': self.formatTime(record, self.datefmt),
                    'level': record.levelname,
                    'message': record.getMessage()
                })


def read_yaml_file(file_path:str=None):
    topic = 'read YAML file'

    try:
        if file_path is None:
            raise Exception("File path cannot be None.")
        
        with open(file_path, 'r') as file:
            return (True, yaml.safe_load(file))
    
    except FileNotFoundError as e:
        logger.error(f'Unable to {topic}. File not found: {file_path}')
        raise (False, e)

    except Exception as e:
        logger.error(f'Unable to {topic}. Reason: {e}')
        raise (False, e)

def read_config_file(file_path:str=None):
    topic = 'read configuration file'

    try:
        result, config_file = read_yaml_file(file_path)

        if not result:
            raise Exception(f'Unable to {topic}. Reason: {config_file}')

        return (True, config_file)

    except Exception as e:
        logger.error(f'Unable to {topic}. Reason: {e}')
        raise (False, e)

def dict_deep_merge(dict1, dict2):
    """Recursively merge two dictionaries, including nested dictionaries."""
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            dict_deep_merge(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1

# 
# Main
# 
if __name__ == '__main__':
    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(LogFormatter(mesg_format='text', json_indent=0))

    logger = logging.getLogger('tcli')
    logger.addHandler(log_stream_handler)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.info('Starting TeamCity script.')
    exit(0)
    # 
    # Merge the configuration and credential files.
    result_config, config = read_config_file('./config.yaml')
    result_creds, creds = read_config_file('./credentials.yaml')

    if not result_config or not result_creds:
        logger.error(f'Unable to read either configuration or credentials file/s. Exiting.')
        exit(1)
    
    import json
    
    logger.info(f'Configuration: {json.dumps(config)}')
    exit(0)

    # Merge the configuration and credential files.
    configuration = dict_deep_merge(config, creds)

    url = configuration['teamcity']['config']['url']
    username = configuration['teamcity']['auth']['username']
    password = configuration['teamcity']['auth']['password']
    
    tc = PyTeamCity(base_url=url, username=username, password=password)

    logger.debug(f'Getting all users with roles in the project scope.')
    result, message, response = tc.get_users(fields='**')

    if not result:
        logger.error(f'{message}')
        exit(1)

    logger.debug(f'Found {len(response["user"])} users with roles in the project scope.')
    
    # 
    # Look for any users with a role in the project scope.
    scope_exact = [ 'p:Risk' ]
    scope_starts_with = [ f'{scope_exact[0]}_' ]   

    for user in response['user']:
        username, roles = user['username'], user['roles']['role']

        for role in roles:
            if role['scope'] in scope_exact or any([role['scope'].startswith(s) for s in scope_starts_with]):
                logger.info(f'Username: {username}\tRoleId: {role["roleId"]}\tScope: {role["scope"]}')
