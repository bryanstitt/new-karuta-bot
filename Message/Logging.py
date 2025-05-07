import logging # log files
import os # environment variables
from datetime import datetime
import re

def setup_logging(log_folder='log'):
    """
    Setup logging configuration.
    """
    log_level = os.getenv('LOG_LEVEL', 20)
    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.WARNING if log_level is None else int(log_level)) # default log level is WARNING
    os.makedirs(log_folder, exist_ok=True)
    log_filename = os.path.join(log_folder, datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"))
    handler = logging.FileHandler(filename=log_filename, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s'))
    LOGGER.addHandler(handler)
    return LOGGER

def cleanup_old_logs(log_folder='log', max_logs=10):
    log_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.log$')
    logs = []

    # Ensure the log folder exists
    if not os.path.isdir(log_folder):
        print(f"Log folder '{log_folder}' does not exist.")
        return

    # Collect valid log files with parsed datetime
    for filename in os.listdir(log_folder):
        match = log_pattern.match(filename)
        if match:
            try:
                log_time = datetime.strptime(match.group(1), '%Y-%m-%d_%H-%M-%S')
                logs.append((log_time, filename))
            except ValueError:
                continue

    # Sort logs by datetime
    logs.sort()

    # Delete oldest logs if over the max allowed
    while len(logs) > max_logs:
        oldest = logs.pop(0)
        file_to_delete = os.path.join(log_folder, oldest[1])
        try:
            os.remove(file_to_delete)
            print(f"Deleted old log: {file_to_delete}")
        except Exception as e:
            print(f"Failed to delete {file_to_delete}: {e}")
