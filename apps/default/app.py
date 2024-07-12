#!/usr/bin/env python3
# 
# Default app for the container.
# 
import os
import socket
import getpass

import modules.apphelper as apphelper

def main():
    ah = apphelper.AppHelper(log_format='text')

    ah._logger.info("Hello from your friendly Python container app!")
    
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