#!/usr/bin/env python3

import json
import os
import time
import signal
import sys
import logging
import logging.handlers
import time
import datetime
import re

# 
# See the README.md file for more information.
# 

_g_app_version:str          = "2.1.0"                           # The version of the app
_p_ev_app_name:str          = "Environment Variable Logger"     # The name of the app
_p_ev_logger_indent:int     = 0                                 # JSON print indentation
_p_ev_logger_interval:int   = 300                               # Interval for emitting the labels
_p_ev_logger_prefix:str     = None                              # Prefix for the environment variables
_p_ev_logger_labels:dict    = {}                                # Labels to be emitted

class JsonFormatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()

        # If the message is a string that can be loaded as a JSON, do it
        if isinstance(message, str):
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                pass

        log_object = {
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': message
        }

        if _p_ev_logger_indent:
            return json.dumps(log_object, indent=_p_ev_logger_indent)
        else:
            return json.dumps(log_object)

def get_labels_from_env():
    labels = {}

    # Extract the _p_ev_logger_prefix, convert to lower case and replace all _ to . characters.
    logger_prefix = _p_ev_logger_prefix.lower().replace("_", ".")

    # Iterate through all environment variables
    for key, value in os.environ.items():

        # Check if the environment variable starts with the expected prefix
        if key.startswith(_p_ev_logger_prefix): 
            
            # Remove the whole prefix from the key. Append later.
            key = key.replace(f"{_p_ev_logger_prefix}_", "")
                      
            # 
            # Determine if the key has a sub-key, indicated by a double underscore:
            #   Yes = <prefix>_<label>__<index>__<sub-label>
            #   No  = <prefix>_<label>           
                        
            # Check if the key has a sub-key.
            if re.search(r"__\d+__", key):
                
                # Split the key into index and sub-label parts.
                parts = key.split("__")
            
                # Extract the label, index, sub-label, and value.
                label = f"{logger_prefix}/" + parts[0].lower().replace("_", ".")
                index = int(parts[1])
                sub_label = parts[2].lower().replace("_", ".")

                # If the label is not already in the labels dictionary, add it.
                if label not in labels:
                    labels[label] = []

                # If the index is greater than the current number of sub-labels, add empty dictionaries until it is not.
                while index >= len(labels[label]):
                    labels[label].append({})

                # Add the sub-label to the label in the labels dictionary.
                labels[label][index][sub_label] = value
            else:
                # Extract the label and value, then add it to the labels dictionary.
                label = f"{logger_prefix}/" + key.lower().replace("_", ".")
                labels[label] = value
    
    return labels

def emit_labels(): 
    # Start emitting the labels at the the _p_ev_logger_interval interval.
    logging.info(f"Starting {_p_ev_app_name} v{_g_app_version}. Emitting labels { 'once only' if _p_ev_logger_interval == 0 else f'every {_p_ev_logger_interval} seconds' }.")
    
    while True:
        # Log the labels as a JSON string.
        logging.info(json.dumps(_p_ev_logger_labels))
        
        # If the interval is 0, emit once only and then exit.
        if _p_ev_logger_interval == 0:
            sys.exit(0)

        # Sleep for the specified interval.
        time.sleep(_p_ev_logger_interval)

def signal_handler(sig, frame):
    logging.info(f"Terminating the {_p_ev_app_name}. Reason: Received {signal.Signals(sig).name}({sig}).")
    sys.exit(0)

if __name__ == "__main__":
    # 
    # Register the signal handler to catch SIGTERM signals.
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 
    # Catch ctrl+c
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if the prefix is set.
    if not "EV_LOGGER_PREFIX" in os.environ:
        print("No prefix found. Please set the appropriate environment variables.")
        exit(1)
    
    # Check at least 1 label env variable configured.
    if len([key for key in os.environ.keys() if key.startswith(os.environ["EV_LOGGER_PREFIX"])]) == 0:
        print("No label environment variables set. Please set the appropriate environment variables.")
        exit(1)
    
    # 
    # Configure logging.
    # 
    logger = logging.getLogger()           # Get the root logger
    logger.setLevel(logging.INFO)          # Set the level for the logger
    
    for handler in logger.handlers[:]:  
        logger.removeHandler(handler)      # Remove all handlers from the root logger

    # Configure either stdout/err or syslog logging. Default to stdout/err.
    handler = logging.StreamHandler()
    if "EV_LOGGER_SYSLOG" in os.environ and os.environ["EV_LOGGER_SYSLOG"] == "1":
        # If the EV_LOGGER_SYSLOG environment variable is set to 1, use the syslog handler.
        handler = logging.handlers.SysLogHandler(address = '/dev/log')
    
    handler.setFormatter(JsonFormatter())   # Set the formatter to the JsonFormatter
    logger.addHandler(handler)             # Add the handler to the logger
    
    
    # 
    # Configure the prefix, the emitting interval and JSON indentation.
    # 
    
    # Configure the prefix ensuring to remove any trailing underscore characters.
    _p_ev_logger_prefix = os.environ["EV_LOGGER_PREFIX"]
    while _p_ev_logger_prefix[-1] == "_":
        _p_ev_logger_prefix = _p_ev_logger_prefix[:-1]
    
    # Configure the emit interval.
    # Default (see above) used if environment variable is missing, not an integer, less than 0 or greater than 1 week.
    emit_interval_max_in_seconds = 604800
    if "EV_LOGGER_PREFIX" in os.environ and os.environ["EV_LOGGER_PREFIX"].isdigit() and 0 <= int(os.environ["EV_LOGGER_PREFIX"]) <= emit_interval_max_in_seconds:
        _p_ev_logger_interval = int(os.environ["EV_LOGGER_PREFIX"])

    # Configure the JSON indentation.
    # Default (see above) used if environment variable is missing, not an integer, or less than 0.
    if "EV_LOGGER_INDENT" in os.environ and os.environ["EV_LOGGER_INDENT"].isdigit() and int(os.environ["EV_LOGGER_INDENT"]) >= 0:
        _p_ev_logger_indent = int(os.environ["EV_LOGGER_INDENT"])
    
    # Retrieve the label environment variables.
    _p_ev_logger_labels = get_labels_from_env()
    
    emit_labels()
