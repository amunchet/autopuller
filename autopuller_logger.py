import logging
import os
import sys

# Set up a logger
LEVEL = logging.WARNING
if os.environ.get("DEBUG_LEVEL"):
    try:
        LEVEL = getattr(logging, os.environ.get("DEBUG_LEVEL"))
    except Exception:
        print("Error with", os.environ.get("DEBUG_LEVEL"))
        print("Setting debug level to WARNING...")
        LEVEL = logging.WARNING


logger = logging.getLogger(__name__)
logger.setLevel(LEVEL)

# Create a file handler and a stream handler
if os.environ.get("REMOTE") == "GITHUB":
    file_handler = logging.FileHandler("/tmp/autopuller")
else:
    file_handler = logging.FileHandler("/var/log/autopuller")

stream_handler = logging.StreamHandler(sys.stderr)

# Set the level for both handlers
file_handler.setLevel(LEVEL)
stream_handler.setLevel(LEVEL)

# Create a formatter and set it for both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
