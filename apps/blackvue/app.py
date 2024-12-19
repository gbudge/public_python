#!/usr/bin/env python3
"""
Blackvue 970 XP Downloader v1.0.0

This script is designed to download video files from a BlackVue dashcam. 
It connects to the dashcam using the specified protocol, IP address, and port, 
retrieves a list of available files, and downloads them to a local directory.

Modules:
    sys
    os
    logging
    json
    requests
    pathlib
    argparse

Classes:
    LogFormatter(logging.Formatter)

Functions:
    get_file_list(protocol: str, ip_host: str, port: int) -> list
    parse_file_list(raw_data: str) -> list
    download_file(protocol: str, ip_host: str, port: int, file_path: str, download_directory: str) -> bool
    main() -> bool
        Entry point of the application. Initializes the logger and logs some information about the environment.

Usage:
    Run the script with the required command-line arguments:
        --host <hostname or IP address>
        --port <port number>
        --protocol <protocol>
        --save-to <output directory>

Example:
    python app.py --host 192.168.1.1 --port 80 --protocol http --save-to downloads
"""

import sys
import os
import logging
import json
import requests # type: ignore
from pathlib import Path
from argparse import ArgumentParser


# Disable the pylint warning about line length > 100 characters.
# pylint: disable=C0301

# Logger class and formatter
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

# Create the logger
LOG_STREAM_HANDLER: logging.StreamHandler
LOG_STREAM_HANDLER = logging.StreamHandler()
LOG_STREAM_HANDLER.setFormatter(LogFormatter(mesg_format='text'))
    
LOGGER: logging.Logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(LOG_STREAM_HANDLER)

def is_camera_reachable(protocol: str, ip_host: str, port: int):
    """
    Checks if a camera is reachable by sending a GET request to the camera's status endpoint.
    Args:
        protocol (str): The protocol to use (e.g., 'http' or 'https').
        ip_host (str): The IP address or hostname of the camera.
        port (int): The port number to use for the connection.
    Returns:
        bool: True if the camera is reachable (status code 200), False otherwise.
    Raises:
        requests.RequestException: If there is an issue with the request.
    """
    
    url = f"{protocol}://{ip_host}:{port}/blackvue_vod.cgi"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        raise e

def get_file_list(protocol: str, ip_host: str, port: int):
    """
    Retrieve the list of files from a BlackVue dashcam.
    Args:
        protocol (str): The protocol to use (e.g., 'http' or 'https').
        ip_host (str): The IP address or hostname of the BlackVue dashcam.
        port (int): The port number to connect to.
    Returns:
        list: A list of files retrieved from the dashcam.
    Raises:
        requests.RequestException: If there is an issue with the HTTP request.
    """

    url = f"{protocol}://{ip_host}:{port}/blackvue_vod.cgi"
    files = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        file_list = response.text

        # Example response:
        # v:3.00
        # n:/Record/20241217_205239_EF.mp4,s:1000000
        # n:/Record/20241217_205239_ER.mp4,s:1000000
        # n:/Record/20241217_205643_NF.mp4,s:1000000
        # n:/Record/20241217_205643_NR.mp4,s:1000000
        
        skip_prefix_list = [
            "#",    # Skip comments
            "v:"    # Skip version information and file names
        ]

        for line in file_list.splitlines():
            LOGGER.debug(f"Processing line: {line}")

            # Skip lines that start with any of the prefixes in the skip_prefix_list
            if any(line.startswith(prefix) for prefix in skip_prefix_list):
                LOGGER.debug(f"Skipping line: {line}")
                continue
            
            #
            # Split line by comma and remove any preceding <letter>: prefix
            #
            #   Example:
            #       Line : n:/Record/20241217_205239_EF.mp4,s:1000000
            #       [0]  : n:/Record/20241217_205239_EF.mp4
            #       [1]  : s:1000000
            #       [3:] : Record/20241217_205239_EF.mp4
            LOGGER.debug(f"Splitting line: {line}")
            line = line.split(",")[0][3:]

            # Append the file path to the list
            LOGGER.debug(f"Adding file: {line}")
            files.append(line)
    except requests.RequestException as e:
        raise e

    return files

def download_file(protocol: str, ip_host: str, port: int, file_path: str, download_directory: str, file_number: int, total_files:int):
    """
    Downloads a file from a specified URL and saves it to a local directory.
    Args:
        protocol (str): The protocol to use (e.g., 'http', 'https').
        ip_host (str): The IP address or hostname of the server.
        port (int): The port number to connect to.
        file_path (str): The path to the file on the server.
        download_directory (str): The local directory where the file will be saved.
    Returns:
        bool: True if the file was downloaded successfully.
    Raises:
        requests.RequestException: If there is an issue with the HTTP request.
    """
    
    #
    # Filename Format:
    #   /<Folder Type>/<YYYYMMDD_HHMMSS>_<Recording Type><Camera ID>.mp4
    #
    #   Folder Type:     Is always 'Record'
    #   YYYYMMDD_HHMMSS: Date and time of the recording
    #   Recording Type:  E = Event, N = Normal, P = Parking, I = Impact, M = Manual, T = Time-lapse
    #   Camera ID:       F = Front, R = Rear
    #
    # Example file_path:
    #   /Record/20241217_205239_EF.mp4
    #

    chunk_size = 16384
    chunk_timeout = 120
    
    mp4_url = f"{protocol}://{ip_host}:{port}/{file_path}"
    save_to = os.path.join(download_directory, file_path)
    save_to_temp = f"{save_to}.bvdownload"
    
    try:
        # Request the file from the dashcam
        response = requests.get(mp4_url, stream=True, timeout=chunk_timeout)
        response.raise_for_status()

        # Get the size of the file in bytes
        mp4_bytes = int(response.headers.get('Content-Length', 0))

        # Create any relative directories if they don't exist
        if not os.path.exists(os.path.dirname(save_to)):
            os.makedirs(os.path.dirname(save_to))
        
        # Check if the file already exists and it's the same size
        if os.path.exists(save_to) and os.path.getsize(save_to) == mp4_bytes:
            return True
        
        # Attempt to download the file to a temporary file
        progress_percentage: float = 0.0
        logged_progress: bool = False

        with open(save_to_temp, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):

                # Update the progress percentage, rounded to 2 decimal place
                progress_percentage += len(chunk) / mp4_bytes * 100
                progress_rounded = round(progress_percentage, 2)

                if progress_rounded % 10 == 0:
                    if not logged_progress:
                        LOGGER.info(f"Progress: {file_number} of {total_files}: {file_path}.. {progress_rounded}%")
                        logged_progress = True
                else:
                    logged_progress = False
                
                file.write(chunk)
            file.close()

        # Rename the temporary file to the final filename
        os.rename(save_to_temp, save_to)

        return True

    except requests.RequestException as e:
        raise e

def main():
    """
    Entry point of the application.
    
    This function initializes the logger and logs some information about the environment.
    """

    # Commandline Parameters
    parser = ArgumentParser(description="Blackvue 970 XP Downloader")
    parser.add_argument("--host", type=str, help="hostname or IP Address of the Blackvue 970 XP")
    parser.add_argument("--port", type=int, default=80, help="port number of the Blackvue 970 XP. Default: 80")
    parser.add_argument("--protocol", type=str, default="http", help="protocol to use for the connection. Default: http")
    parser.add_argument("--save-to", metavar="PATH", type=str, default="downloads", help="directory where to save the files. Default: downloads")
    args = parser.parse_args()

    # Check for required parameters
    if not args.protocol:
        LOGGER.error("Protocol is required")
        return False
    
    if not args.host:
        LOGGER.error("Hostname or IP Address is required")
        return False

    if not args.port:
        LOGGER.error("Port number is required")
        return False

    if not args.save_to:
        LOGGER.error("Output directory is required")
        return False
    
    #
    # Start the application
    #
    LOGGER.info("Blackvue 970 XP Downloader started")

    # Check if the output directory exists and is writable
    if not os.path.exists(args.save_to) or not os.access(args.save_to, os.W_OK):
        LOGGER.error(f"Output directory does not exist or is not writable: {args.save_to}")
        return False

    # Check if the camera is reachable
    try:
        if not is_camera_reachable(args.protocol, args.host, args.port):
            LOGGER.error(f"Camera is not reachable at {args.protocol}://{args.host}:{args.port}")
            return False
    except requests.RequestException as e:
        LOGGER.error(f"Failed to connect to the camera. Reason: {e}")
        return False

    # Get the list of files available on the Blackvue 970 XP
    file_list = get_file_list(args.protocol, args.host, args.port)
    if not file_list:
        LOGGER.error("No files found on the camera")
        return False
    
    # Download the files from the Blackvue 970 XP
    total_files = len(file_list)
    file_number = 0
    for file_path in file_list:
        file_number += 1

        try:
            res = download_file(args.protocol, args.host, args.port, file_path, args.save_to, file_number, total_files)
            if not res:
                raise (f"Failure: {file_number} of {total_files}: {file_path}.")
                
        except requests.RequestException as e:
            LOGGER.error(f"Failure: {file_number} of {total_files}: {file_path}. Reason: {e}")
            return False
        
        LOGGER.info(f"Complete: {file_number} of {total_files}: {file_path}")
if __name__ == "__main__":
    if not main():
        sys.exit(1)
    
    sys.exit(0)
