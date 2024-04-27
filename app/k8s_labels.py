import json
import os
import time
import signal
import sys
import logging
import time
import argparse
import datetime

# 
# See the README.md file for more information.
# 

json_indent = None      # JSON print indentation
emit_interval = None    # Interval for emitting the labels

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

        if json_indent:
            return json.dumps(log_object, indent=json_indent)
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

    # Iterate through all environment variables
    for key, value in os.environ.items():

        # Check if the environment variable starts with the expected prefix
        if key.startswith("APP_KUBERNETES_IO_"):
            # Split the key into parts.
            parts = key.split("_")

            # Check if it is a top-level label
            if len(parts) == 4:
                # Extract the label and value, then add it to the labels dictionary.
                label = "app.kubernetes.io/" + parts[3].lower().replace("-", ".")
                labels[label] = value
            
            # Check if it is a sub-label
            elif len(parts) == 6:
                # Extract the label, index, sub-label, and value.
                label = "app.kubernetes.io/" + parts[3].lower().replace("-", ".")
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

        # Print a warning if the labels are empty or only contains the interval key.
        if len(labels) == 0 or (len(labels) == 1 and "interval" in labels):
            logging.warning("No Kubernetes labels found. Please set the appropriate environment variables.")
        else:
            # Log the labels as a JSON string.
            logging.info(json.dumps(labels))
            
        time.sleep(emit_interval)

def signal_handler(sig, frame):
    logging.info("Terminating the Kubernetes Label Emitter. Received SIGTERM signal.")
    logging.info(f"sig: {sig}, frame: {frame}")
    sys.exit(0)

def export_sample_environment_variables():
    # Log the sample environment variables.
    logging.info("Exporting sample environment variables.")

    os.environ["APP_KUBERNETES_IO_INSTANCE"] = "my-instance"
    os.environ["APP_KUBERNETES_IO_MANAGED-BY"] = "my-team"
    os.environ["APP_KUBERNETES_IO_PART-OF"] = "my-collection"
    os.environ["APP_KUBERNETES_IO_INVENTORY_0_NAME"] = "my-app"
    os.environ["APP_KUBERNETES_IO_INVENTORY_0_VERSION"] = "v1"
    os.environ["APP_KUBERNETES_IO_INVENTORY_0_COMPONENT"] = "my-component"
    os.environ["APP_KUBERNETES_IO_INVENTORY_1_NAME"] = "my-app2"
    os.environ["APP_KUBERNETES_IO_INVENTORY_1_VERSION"] = "v2"
    os.environ["APP_KUBERNETES_IO_INVENTORY_1_COMPONENT"] = "my-component2"

if __name__ == "__main__":
    # Use argparser to get the indent value.
    parser = argparse.ArgumentParser(description='Kubernetes Label Emitter')
    parser.add_argument('--indent', type=int, default=None, help='The number of spaces for indentation in the output JSON')
    parser.add_argument('--interval', type=int, default=300, help='The number of seconds between emitting the output')
    args = parser.parse_args()

    json_indent = args.indent
    emit_interval = args.interval

    logging.info("Starting Kubernetes Label Emitter. Interval: %s seconds", emit_interval)
    signal.signal(signal.SIGTERM, signal_handler)       # Register the signal handler to catch SIGTERM signals.
    # export_sample_environment_variables()               # Export the sample environment variables.  
    emit_labels()                                       # Start emitting the labels. 