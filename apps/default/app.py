#!/usr/bin/env python3
# 
# Default app for the container.
# 
import os
import socket
import getpass
import logging
import json

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


def main():
    log_stream_handler: logging.StreamHandler
    logger: logging.Logger

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(LogFormatter(mesg_format='text'))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_stream_handler)

    logger.info("Hello from your friendly Python container app!")
    
    # Hostname (usually the container ID)
    logger.info(f"Hostname: {socket.gethostname()}")
    
    # Current user
    logger.info(f"Running as user: {getpass.getuser()}")
    
    # Current working directory
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # List files in the current directory
    logger.info("Files in the current directory:")
    for file in os.listdir():
        logger.info(f" - {file}")
    
    # Print some environment variables
    logger.info("Some environment variables:")
    for var in ["HOME", "PATH"]:
        logger.info(f"{var}: {os.environ.get(var)}")

if __name__ == "__main__":
    main()