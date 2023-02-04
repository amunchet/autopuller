import logging
import os

# Set up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and a stream handler
if os.environ.get("REMOTE") == "GITHUB":
    file_handler = logging.FileHandler("/tmp/autopuller")
else:
    file_handler = logging.FileHandler("/var/log/autopuller")

stream_handler = logging.StreamHandler()

# Set the level for both handlers
file_handler.setLevel(logging.INFO)
stream_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
