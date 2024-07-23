#!/usr/bin/env python3
"""
Default app for the container. Demonstrates using the custom logger.

Version: 1.0.1

Args: None
"""
import os
import socket
import getpass
import logging
import json

# Disable the pylint warning about line length > 100 characters.
# pylint: disable=C0301

class LogFormatter(logging.Formatter):
    """
    Custom log formatter that formats log records based on the specified format options.

    Args:
        date_format (str, optional): The format string for the log record's timestamp. Defaults to '%Y-%m-%d %H:%M:%S'.
        mesg_format (str, optional): The format for the log message. Can be 'text', 'json', or 'csv'. Defaults to 'json'.
        json_indent (int, optional): The number of spaces to use for indentation in the JSON format. Must be between 0 and 10. Defaults to 0.
    """

    datefmt:str = None
    mesgfmt:str = None
    indent:int = None

    def __init__(self, date_format:str=None, mesg_format:str=None, json_indent:int=None):
        # Call the parent class's __init__ method
        super().__init__()

        if not date_format:
            self.datefmt = '%Y-%m-%d %H:%M:%S'

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
    """
    Entry point of the application.
    
    This function initializes the logger and logs some information about the environment.
    """
    log_stream_handler: logging.StreamHandler
    logger: logging.Logger

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(LogFormatter(mesg_format='json'))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_stream_handler)

    logger.info("Hello from your friendly Python container app!")

    # Hostname (usually the container ID)
    logger.info("Hostname: %s", socket.gethostname())

    # Current user
    logger.info("Running as user: %s", getpass.getuser())

    # Current working directory
    logger.info("Current working directory: %s", os.getcwd())

    # List files in the current directory, if any exist.
    if os.listdir(os.getcwd()):
        log_event = "Files in the current directory: "
        for f in os.listdir(os.getcwd()):
            log_event += f"{f}, "

        logger.info(log_event[:-2])
    else:
        logger.info("No files in the current directory.")

    # Print some environment variables
    for var in ["HOME", "PATH"]:
        logger.info("%s: %s", var, os.environ.get(var))

if __name__ == "__main__":
    main()
