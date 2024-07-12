import logging
import json
import yaml
import os

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

class AppHelper:
    _log_stream_handler: logging.StreamHandler = None
    _logger: logging.Logger = None

    def __init__(self, log_name:str=__name__, log_level:int=logging.INFO, log_format:str='text'):
        _log_stream_handler = logging.StreamHandler()
        _log_stream_handler.setFormatter(LogFormatter(mesg_format=log_format))

        _logger = logging.getLogger(log_name)
        _logger.setLevel(log_level)
        _logger.addHandler(_log_stream_handler)

    @staticmethod
    def my_internal_method(self):
        pass


    def read_yaml_file(self, file_path:str=None):
        topic = 'read YAML file'

        try:
            if file_path is None:
                raise Exception("File path cannot be None.")
            
            with open(file_path, 'r') as file:
                return (True, yaml.safe_load(file))
        
        except FileNotFoundError as e:
            self._logger.error(f'Unable to {topic}. File not found: {file_path}')
            raise (False, e)

        except Exception as e:
            self._logger.error(f'Unable to {topic}. Reason: {e}')
            raise (False, e)

    def read_config_file(self, file_path:str=None):
        topic = 'read configuration file'

        try:
            if file_path is None:
                raise Exception("File path cannot be None.")
            
            with open(file_path, 'r') as file:
                return (True, json.load(file))
        
        except FileNotFoundError as e:
            self._logger.error(f'Unable to {topic}. File not found: {file_path}')
            raise (False, e)

        except Exception as e:
            self._logger.error(f'Unable to {topic}. Reason: {e}')
            raise (False, e)
