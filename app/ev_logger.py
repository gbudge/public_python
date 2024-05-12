import json
import os
import time
import signal
import sys
import logging
import time
import datetime

# 
# See the README.md file for more information.
# 

ev_app_version      = "2.0.0"                       # The version of the app
ev_app_name         = "Environment Variable Logger" # The name of the app
ev_logger_indent    = None                          # JSON print indentation
ev_logger_interval  = None                          # Interval for emitting the labels
ev_logger_prefix    = None                          # Prefix for the environment variables

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

        if ev_logger_indent:
            return json.dumps(log_object, indent=ev_logger_indent)
        else:
            return json.dumps(log_object)

# Set up logging.
logger = logging.getLogger()            # Get the root logger
for handler in logger.handlers[:]:  
    logger.removeHandler(handler)       # Remove all handlers from the root logger
logger.setLevel(logging.INFO)           # Set the level for the logger
handler = logging.StreamHandler()       # Create a handler that writes to stdout
handler.setFormatter(JsonFormatter())   # Set the formatter to the JsonFormatter
logger.addHandler(handler)              # Add the handler to the logger

def get_labels_from_env():
    labels = {}

    # Extract the EV_LOGGER_PREFIX, convert to lower case and replace all _ to . characters.
    logger_prefix = ev_logger_prefix.lower().replace("_", ".")

    # Iterate through all environment variables
    for key, value in os.environ.items():

        # Check if the environment variable starts with the expected prefix
        if key.startswith(ev_logger_prefix):
            # Split the key into parts.
            parts = key.split("_")

            # Check if it is a top-level label
            if len(parts) == 4:
                # Extract the label and value, then add it to the labels dictionary.
                label = f"{logger_prefix}/" + parts[3].lower().replace("-", ".")
                labels[label] = value
            
            # Check if it is a sub-label
            elif len(parts) == 6:
                # Extract the label, index, sub-label, and value.
                label = f"{logger_prefix}/" + parts[3].lower().replace("-", ".")
                index = int(parts[4])
                sub_label = parts[5].lower().replace("-", ".")

                # If the label is not already in the labels dictionary, add it.
                if label not in labels:
                    labels[label] = []

                # If the index is greater than the current number of sub-labels, add empty dictionaries until it is not.
                while index >= len(labels[label]):
                    labels[label].append({})

                # Add the sub-label to the label in the labels dictionary.
                labels[label][index][sub_label] = value

    return labels

def emit_labels():
    # Continuously emit the labels at the specified interval.
    while True:
        labels = get_labels_from_env()

        # Print an error if the labels are empty or only contains the interval key.
        if len(labels) == 0 or (len(labels) == 1 and "interval" in labels.to_lower()):
            logging.error("No labels found. Please set the appropriate environment variables.")
            exit(1)
        
        # Log the labels as a JSON string.
        logging.info(json.dumps(labels))
        
        # If the interval is 0, emit once only and then exit.
        if ev_logger_interval == 0:
            sys.exit(0)

        # Sleep for the specified interval.
        time.sleep(ev_logger_interval)

def signal_handler(sig, frame):
    logging.info(f"Terminating the {ev_app_name}. Received SIGTERM signal.")
    logging.info(f"sig: {sig}, frame: {frame}")
    sys.exit(0)

if __name__ == "__main__":
    # Register the signal handler to catch SIGTERM signals.
    signal.signal(signal.SIGTERM, signal_handler)

    # Emit interval. If missing, not an integer, less than 0 or greater than 1 week, use the default value.
    ev_logger_interval = 300
    if "EV_LOGGER_INTERVAL" in os.environ and os.environ["EV_LOGGER_INTERVAL"].isdigit() and 0 <= int(os.environ["EV_LOGGER_INTERVAL"]) <= 604800:
        ev_logger_interval = int(os.environ["EV_LOGGER_INTERVAL"])

    # Json indentation. If missing, not an integer, or less than 0, use the default value.
    ev_logger_indent = 0
    if "EV_LOGGER_INDENT" in os.environ and os.environ["EV_LOGGER_INDENT"].isdigit() and int(os.environ["EV_LOGGER_INDENT"]) >= 0:
        ev_logger_indent = int(os.environ["EV_LOGGER_INDENT"])
    
    # Check if the prefix is set. If not, print an error and exit.
    if "EV_LOGGER_PREFIX" not in os.environ:
        logging.error("No prefix found. Please set the appropriate environment variables.")
        exit(1)
    
    # Set the prefix to the environment variable.
    ev_logger_prefix = os.environ["EV_LOGGER_PREFIX"]

    # Remove all trailing _ characters.
    while ev_logger_prefix[-1] == "_":
        ev_logger_prefix = ev_logger_prefix[:-1]

    # Start emitting the labels. 
    logging.info(f"Starting {ev_app_name} v{ev_app_version}. Emitting labels {
        'once only' if ev_logger_interval == 0 else f'every {ev_logger_interval} seconds'
    }.")

    emit_labels()
